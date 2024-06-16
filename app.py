from flask import Flask, request, render_template, jsonify, send_file
from service_streamer import ThreadedStreamer
import zipfile
import os
from model import *
import shutil
from threading import Thread, Lock
import time
import torch
import service_streamer

service_streamer.service_streamer.WORKER_TIMEOUT = 7200
model = load_model()
llm = translation_model()
transcribe_fn = RequestTranscribe(model, llm)
app = Flask(__name__)
streamer = ThreadedStreamer(transcribe_fn.transcribe, batch_size=32, max_latency=0.5)

progress = 0
output_zip = 'transcripts_result.zip'
start_time = None
processing_lock = Lock()
current_users = 0

@app.route('/')
def my_form():
    gpu_usage = get_gpu_usage()
    return render_template('index.html', gpu_usage=gpu_usage, user_count=current_users)

@app.route('/result', methods=['POST'])
def file_upload():
    global progress, start_time, current_users
    progress = 0
    start_time = time.time()

    if processing_lock.locked():
        return render_template('server_busy.html')

    f = request.files['file']
    f.save(f.filename)

    current_users += 1
    thread = Thread(target=process_file, args=(f.filename,))
    thread.start()

    return render_template('progress.html')

def process_file(filename):
    global progress, start_time, current_users
    with processing_lock:
        text, transcript, language = transcribe_old(filename, model, llm)
        progress = 100
        current_users -= 1

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    global progress, start_time, current_users
    progress = 0
    start_time = time.time()

    if processing_lock.locked():
        return render_template('server_busy.html')

    files = request.files.getlist('folder')
    folder_path = 'uploaded_folder'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save uploaded files to the folder
    for f in files:
        file_path = os.path.join(folder_path, f.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
        f.save(file_path)

    current_users += 1
    thread = Thread(target=process_folder, args=(folder_path,))
    thread.start()

    return render_template('progress.html')

def process_folder(folder_path):
    global progress, output_zip, start_time, current_users
    with processing_lock:
        output_dir = 'transcripts_result'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        files = [os.path.join(root, file) for root, _, files in os.walk(folder_path) for file in files]
        total_files = len(files)

        for idx, file_path in enumerate(files):
            transcribe_old(file_path, model, llm)
            progress = (idx + 1) / total_files * 100

        # Create a zip file of the results
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    zipf.write(os.path.join(root, file))

        # Clean up the uploaded folder (leave the result files for download)
        shutil.rmtree(folder_path)

        # Mark the progress as complete
        progress = 100
        current_users -= 1

@app.route('/progress')
def progress_status():
    global progress, start_time
    elapsed_time = time.time() - start_time
    if progress > 0:
        estimated_total_time = elapsed_time / (progress / 100)
        estimated_time_remaining = estimated_total_time - elapsed_time
    else:
        estimated_time_remaining = "calculating..."

    return jsonify(progress=progress, estimated_time=0)

@app.route('/status')
def status():
    gpu_usage = get_gpu_usage()
    return jsonify(gpu_usage=gpu_usage, user_count=current_users, busy=processing_lock.locked())

@app.route('/folder_results')
def folder_results():
    return render_template('folder_results.html')

@app.route('/download_results')
def download_results():
    global output_zip
    return send_file(output_zip, as_attachment=True)

def get_gpu_usage():
    if torch.cuda.is_available():
        gpu_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
        return f"{gpu_usage:.2f}%"
    return "N/A"

if __name__ == '__main__':
    app.run(host='0.0.0.0')

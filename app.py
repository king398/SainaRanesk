from flask import Flask, request, render_template, jsonify
from service_streamer import ThreadedStreamer
from model import *
import service_streamer

service_streamer.service_streamer.WORKER_TIMEOUT = 7200
model = load_model()
app = Flask(__name__)
streamer = ThreadedStreamer(request_transcribe.transcribe, batch_size=8, max_latency=0.1)


@app.route('/')
def my_form():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def file_upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        text, transcript,language = transcribe_old(f.filename,model)
    # play audio file audio.wav

    return render_template('result.html', text=transcript, results_text=text,)


@app.route('/transcribe', methods=['POST'])
def transcribe_form():
    f = request.files['file']
    x = streamer.predict([f])

    return jsonify({'transcript': x})


if __name__ == '__main__':
    app.run(host='0.0.0.0')

from flask import Flask, request, render_template

from model import *
model = load_model()
app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def file_upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        print(f.filename)
        transcript, text = transcribe(f.filename, model)
    # play audio file audio.wav

    return render_template('result.html', text=transcript, results_text=text    )


if __name__ == '__main__':
    app.run(debug=True)

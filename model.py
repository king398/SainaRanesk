import whisper
from typing import Iterator
import librosa
import soundfile as sf
import os
import argparse

os.makedirs("/home/transcripts", exist_ok=True)


def load_model():
    model = whisper.load_model("models/large-v2.pt")
    return model


def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)
    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000
    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000
    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000
    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"


def transcript_timestamp(transcript: Iterator[dict], path):
    path = path.split('/')[-1]
    path = path.split('.')[0]
    text_file = open(f"/home/transcripts/{path}.txt", "w")
    for segment in transcript:
        text_file.write(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])} "
            f"Text: {segment['text'].strip().replace('-->', '->')}\n",
        )
    text_file.close()
    return f"/home/transcripts/{path}.txt"


def transcribe(path, model):
    print(f"Reducing Noise")
    print(f"Transcribing... {path}")

    result = model.transcribe(path, task='translate', verbose=True, no_speech_threshold=0.25,
                              condition_on_previous_text=False)
    text_file = transcript_timestamp(result["segments"], path)

    with open(text_file, "r") as f:
        text = f.read()
    p = 0

    formatted_text = ""
    for i in result['text'].split(' '):
        if p % 40 == 0:
            formatted_text += "\n"
        formatted_text += i
        formatted_text += " "
        p += 1
    print(f"Transcription complete. Saved it to {text_file} ")
    # delete path and audio.wav
    os.remove(path)
    return text, formatted_text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='path to audio file', nargs='+')
    args = parser.parse_args()

    model = load_model()
    for path in args.path:
        transcribe(path, model)

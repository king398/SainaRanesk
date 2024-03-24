import whisper
from typing import Iterator
import librosa
import soundfile as sf
import os
import argparse
from joblib import Parallel, delayed

os.makedirs("transcripts_result", exist_ok=True)


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


def transcript_timestamp(transcript: Iterator[dict], input_file_path, output_file_path):
    with open(output_file_path, "w") as out_file:
        for segment in transcript:
            out_file.write(
                f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])} "
                f"Text: {segment['text'].strip().replace('-->', '->')}\n"
            )


def transcript_timestamp_old(transcript: Iterator[dict], path):
    path = path.split('/')[-1]
    path = path.split('.')[0]
    text_file = open(f"transcripts_result/{path}.txt", "w")
    for segment in transcript:
        text_file.write(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])} "
            f"Text: {segment['text'].strip().replace('-->', '->')}\n",
        )
    text_file.close()
    return f"transcripts_result/{path}.txt"


def convert_to_wav(path):
    data, samplerate = librosa.load(path, sr=16000)
    sf.write('audio.wav', data, samplerate)


def transcribe_old(path, model):
    print(f"Transcribing... {path}")
    convert_to_wav(path)
    audio = whisper.load_audio("audio.wav")
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, n_mels=80).to(model.device)
    _, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)

    result = model.transcribe('audio.wav', task='translate', verbose=True, no_speech_threshold=0.25,
                              condition_on_previous_text=False, )
    text_file = transcript_timestamp_old(result["segments"], path)

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
    os.remove('audio.wav')
    return formatted_text, text, language


class request_transcribe:
    def __init__(self, model_whisper):
        self.model = model_whisper

    def transcript_timestamp(self, transcript: Iterator[dict], path):
        path = path.split('/')[-1]
        path = path.split('.')[0]
        text_file = open(f"transcripts_result/{path}.txt", "w")
        for segment in transcript:
            text_file.write(
                f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])} "
                f"Text: {segment['text'].strip().replace('-->', '->')}\n",
            )
        text_file.close()
        return f"transcripts_result/{path}.txt"

    def transcribe(self, paths):
        text_final = []

        for PATH in paths:
            result = self.model.transcribe(PATH, task='translate', verbose=True, no_speech_threshold=0.25,
                                           condition_on_previous_text=False, )
            text_file = self.transcript_timestamp(result["segments"], PATH)
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
            os.remove(PATH)
            text_final.append(formatted_text)

        return text_final


def transcribe(path, model, output_dir="transcripts_result"):
    output_dir_chinese = f"{output_dir}/chinese"
    output_dir_english = f"{output_dir}/english"
    os.makedirs(output_dir_english, exist_ok=True)
    os.makedirs(output_dir_chinese, exist_ok=True)
    print(f"Transcribing... {path}")
    convert_to_wav(path)

    result = model.transcribe('audio.wav', task='translate', verbose=True, no_speech_threshold=0.25,
                              condition_on_previous_text=False)
    result_chinese = model.transcribe('audio.wav', task='transcribe', verbose=True, no_speech_threshold=0.25,
                                      condition_on_previous_text=False)
    output_file_path = os.path.join(output_dir_english,
                                    os.path.basename(path).replace(os.path.splitext(path)[1], '.txt'))
    output_file_path_chinese = os.path.join(output_dir_chinese,
                                            os.path.basename(path).replace(os.path.splitext(path)[1],
                                                                           '.txt'))
    transcript_timestamp(result["segments"], path, output_file_path)
    transcript_timestamp(result_chinese["segments"], path, output_file_path_chinese)

    print(f"Transcription complete. Saved it to {output_dir}")
    os.remove('audio.wav')


def process_directory(input_dir, output_dir, model):
    accepted_audio_extensions = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".avi")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(accepted_audio_extensions):
                input_file_path = os.path.join(root, file)
                transcribe(input_file_path, model, output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process audio files for transcription.')
    parser.add_argument('--path', default=".", help='path to audio file or directory', nargs='*')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser("~/Downloads/transcripts"),
                        help='Output directory for saving transcripts.')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    model = load_model()  # load model

    if os.path.isdir(args.path[0]):
        process_directory(args.path[0], args.output_dir, model)
    else:
        for path in args.path:
            transcribe(path, model, args.output_dir)

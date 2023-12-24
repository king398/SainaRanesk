import whisper
from typing import Iterator
import librosa
import soundfile as sf
import os
import argparse
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from llama_cpp import Llama

os.makedirs("transcripts_result", exist_ok=True)

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32


def load_model():
    model_id = "Mithilss/whisper-large-v3-chinese-finetune-epoch-3-final"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, use_flash_attention_2=True, low_cpu_mem_usage=True
    )
    model.use_cache = True
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=448,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device,
        generate_kwargs={"task": "transcribe", "language": "Chinese", "repetition_penalty": 2.0},

    )
    return pipe


def load_translation_model():
    llm = Llama(model_path='models/qwen-chat-14B-Q8_0.gguf', n_ctx=8000, main_gpu=1, n_gpu_layers=-1,
                n_threads=32, tensor_split=[0.3, 0.7], verbose=True)
    return llm


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


def preprocess_files(paths):
    paths_to_save = []
    wav_paths = []
    for i, path_raw in enumerate(paths):
        path_raw.save(path_raw.filename)
        data, samplerate = librosa.load(path_raw.filename, sr=16000)
        path_raw = path_raw.split('.')[0]
        sf.write(f"{path_raw}.wav", data, samplerate)
        paths_to_save.append(f"{path_raw}.wav")

        wav_paths.append(f"{path_raw}.wav")
        print(f"Saved {path_raw.filename}")

    return paths_to_save, wav_paths


def transcribe_old(path, model):
    print(f"Transcribing... {path}")
    convert_to_wav(path)
    audio = whisper.load_audio("audio.wav")
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, n_mels=128).to(model.device)
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
    def __init__(self, model_whisper, model_translation):
        self.model = model_whisper
        self.translation_llm = model_translation

    def transcribe(self, paths):
        text_final = []

        for i, path in enumerate(paths):
            text_final.append(transcribe(path, self.model, self.translation_llm, "transcripts_result"))

        return text_final


def format_result(result, translation_llm):
    text = ""
    for i in result['chunks']:
        text_prompt = f"""<|im_start|>system
You are Qwen-14b , a specially designed chatbot for translating chinese text into english. 
You will not converse with the user. You will only provide the translation of the text given to you
 and say nothing else. End your translation with special token known as  <end> <|im_end|>
<|im_start|>user
Translate this following sentence to english.- {i['text']}<|im_end|>
<|im_start|>assistant
The English translation of this text is as follows - """

        translated = \
            translation_llm(text_prompt, max_tokens=128, echo=False, stream=False, stop=["<|im_end|>", "<end>"])[
                'choices'][0]['text']
        print(f" Text {i['text']}")
        print(f" Translated {translated}")
        text += f"{i['timestamp'][0]}-{i['timestamp'][1]}:{translated}\n"

    return text


def transcribe(path, model, translation_llm, output_dir="transcripts_result"):
    print(f"Transcribing... {path}")
    result = model(path)
    print(result)
    output_file_path = os.path.join(output_dir, os.path.basename(path).replace(os.path.splitext(path)[1], '.txt'))
    text = format_result(result, translation_llm)

    with open(output_file_path, "w") as f:
        f.write(text)

    print(f"Transcription complete. Saved it to {output_file_path}")

    # os.remove(path)
    return text


def process_directory(input_dir, output_dir, model):
    accepted_audio_extensions = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".avi")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(accepted_audio_extensions):
                input_file_path = os.path.join(root, file)
                transcribe(input_file_path, model, translation_model, output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process audio files for transcription.')
    parser.add_argument('--path', default=".", help='path to audio file or directory', nargs='*')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser("~/Downloads/transcripts"),
                        help='Output directory for saving transcripts.')
    args = parser.parse_args()

    model = load_model()
    translation_model = load_translation_model()
    if os.path.isdir(args.path[0]):
        process_directory(args.path[0], args.output_dir, model)
    else:
        for path in args.path:
            transcribe(path, model, translation_model, args.output_dir)

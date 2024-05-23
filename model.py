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


def load_model():
    model_id = "models/whisper-large-v2"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=15,
        batch_size=16,
        return_timestamps=True,
        torch_dtype=torch_dtype,
        device=device,
        return_language=True,

    )

    return pipe


def translation_model():
    llm = Llama("models/qwen1_5-32b-chat-q4_k_m.gguf", n_gpu_layers=-1, main_gpu=1, tensor_split=[0.2, 0.8],
                n_ctx=8000)
    return llm


base_prompt = """
Please translate the Chinese text provided within the <text> tags to English, keeping the original timestamps intact. The text provided below is just an example to demonstrate the format. Specifically:

Preserve each timestamp exactly as it appears in the original text, including the arrows (-->) and any spaces. For example:
45.32--> 47.32 : 那是谁？ Eagle 在这里吗？
Should be translated as:
45.32--> 47.32 : Who's that? Is Eagle here?
Translate all the text that comes after each timestamp into English.
Maintain the same order of the translated text and timestamps as in the original Chinese. For example:
45.32--> 47.32 : 那是谁？ Eagle 在这里吗？
48.24--> 50.68 : 这些是时间戳，请在翻译中给出示例。
Should be translated as:
45.32--> 47.32 : Who's that? Is Eagle here?
48.24--> 50.68 : These are timestamps, please provide examples in the translation.

Remember, the above text is just an example to illustrate the format. The actual Chinese text to be translated will be provided within <text> and </text> tags. For example:
<text>
45.32--> 47.32 : 那是谁？ Eagle 在这里吗？
48.24--> 50.68 : 这些是时间戳，请在翻译中给出示例。
</text>
Enclose your entire translation within <translated> and </translated> tags. Do not add any additional explanations or comments outside of these tags.
<text>**{Text}**<text>
"""


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


def transcript_timestamp(transcript: Iterator[dict], output_file_path):
    with open(output_file_path, "w") as out_file:
        for segment in transcript:
            out_file.write(f"{segment['timestamp'][0]}--> {segment['timestamp'][1]}: {segment['text'].strip()}\n")


def transcript_timestamp_text(transcript: Iterator[dict], path):
    with open(f"transcripts_result/{path}.txt", "w") as out_file:
        out_file.write(f"Language {transcript[0]['language']}\n")
        for segment in transcript:
            out_file.write(f"{segment['timestamp'][0]}--> {segment['timestamp'][1]} :  {segment['text'].strip()}\n")
    return f"transcripts_result/{path}.txt"


def convert_to_wav(path):
    data, samplerate = librosa.load(path, sr=16000)
    sf.write('audio.wav', data, samplerate)


def transcribe_old(path, model, llm):
    print(f"Transcribing... {path}")
    convert_to_wav(path)

    result = model('audio.wav', generate_kwargs={"task": "transcribe"},
                   return_timestamps=True)
    text_file = transcript_timestamp_text(result['chunks'], path)

    with open(text_file, "r") as f:
        text = f.read()
    text = llm.create_chat_completion([
        {"role": "system",
         "content": "You are an assistant who perfectly Translate the following text from Chinese to English."
                    "Under No circumstances should you provide an output which is chinese. "
                    "All the chinese in the input must be translated to english"},
        {
            "role": "user",
            "content": base_prompt.format(Text=text)
        }], max_tokens=1536, repeat_penalty=1.05, temperature=0.1, top_p=20, top_k=20)['choices'][0]['message'][
        'content']
    with open(text_file, "w") as f:
        f.write(text)
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
    print(result['chunks'][0]['language'])
    return formatted_text, text, result['chunks'][0]['language']


class RequestTranscribe:
    def __init__(self, model_whisper, llm):
        self.model = model_whisper
        self.llm = llm

    def transcribe(self, paths):
        text_final = self.model(paths, generate_kwargs={"task": "transcribe", "language": "chinese"},
                                return_timestamps=True)
        texts = []
        translated_texts = []
        for index, i in enumerate(text_final):
            text = transcript_timestamp_text(i['chunks'], paths[index])
            with open(text, "r") as f:
                texts.append(f.read())
        for i in range(len(texts)):
            generated = self.llm.create_chat_completion([
                {"role": "system",
                 "content": "You are an assistant who perfectly Translate the following text from Chinese to English.Under No circumstances should you provide an output which is chinese"},
                {
                    "role": "user",
                    "content": base_prompt.format(Text=texts[i])
                }], max_tokens=1024, temperature=0.6)['choices'][0]['message']['content']
            translated_texts.append(generated)

        return translated_texts


def transcribe(path, model, llm, output_dir="transcripts_result", ):
    print(f"Transcribing... {path}")
    convert_to_wav(path)

    result = model('audio.wav', generate_kwargs={"task": "transcribe"}, return_timestamps=True)
    output_file_path = os.path.join(output_dir, path.split('/')[-1].split('.')[0] + ".txt")
    transcript_timestamp(result['chunks'], output_file_path)
    with open(output_file_path, "r") as f:
        text = f.read()
    text = llm.create_chat_completion([
        {"role": "system",
         "content": "You are an assistant who perfectly Translate the following text from Chinese to English.Under No circumstances should you provide an output which is chinese"},
        {
            "role": "user",
            "content": base_prompt.format(Text=text)
        }], max_tokens=1024, temperature=0.6)['choices'][0]['message']['content']
    with open(output_file_path, "w") as f:
        f.write(text)
    print(f"Transcription complete. Saved it to {output_dir}")
    os.remove('audio.wav')


def process_directory(input_dir, output_dir, model, llm):
    accepted_audio_extensions = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".avi")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(accepted_audio_extensions):
                input_file_path = os.path.join(root, file)
                transcribe(input_file_path, model, llm, output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process audio files for transcription.')
    parser.add_argument('--path', default=".", help='path to audio file or directory', nargs='*')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser("~/Downloads/transcripts"),
                        help='Output directory for saving transcripts.')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    model = load_model()  # load model
    llm = translation_model()

    if os.path.isdir(args.path[0]):
        process_directory(args.path[0], args.output_dir, model, llm)
    else:
        for path in args.path:
            transcribe(path, model, llm, args.output_dir)

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
from pydub import AudioSegment
import os
import argparse

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "models/whisper-large-v3-chinese-finetune-epoch-3-final"


def load_model():
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
        max_new_tokens=256,
        chunk_length_s=30,
        batch_size=16,
        return_timestamps=False,
        torch_dtype=torch_dtype,
        device=device,
        generate_kwargs={"language": "chinese", 'repetition_penalty': 2.0}
    )
    return pipe


def split_audio(file_path, chunk_length_ms=30000, output_dir="chunks"):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Split audio into chunks
    chunk_count = len(audio) // chunk_length_ms
    chunk_paths = []
    for i in range(0, chunk_count):
        chunk_start = i * chunk_length_ms
        chunk_end = chunk_start + chunk_length_ms
        chunk = audio[chunk_start:chunk_end]

        # Export chunk to file
        chunk_file_name = f"{os.path.basename(file_path).split('.')[0]}_chunk{i}.mp3"
        chunk_path = os.path.join(output_dir, chunk_file_name)
        chunk.export(chunk_path, format="mp3")
        chunk_paths.append(chunk_path)

    return chunk_paths


def transcribe(model, output_dir, file):
    print(f"Transcribing... {file}")

    chunk_paths = split_audio(file)
    for i, chunk_path in enumerate(chunk_paths):
        result = model(chunk_path)
        output_file_path = f"{output_dir}/{os.path.basename(chunk_path).split('.')[0]}_chunk_{i}.txt"
        with open(output_file_path, "w") as f:
            f.write(result["text"])
        print(f"Transcription complete. Saved it to {output_file_path}")
        os.remove(chunk_path)


def process_directory(input_dir, output_dir, model):
    accepted_audio_extensions = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".avi")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(accepted_audio_extensions):
                input_file_path = os.path.join(root, file)
                print(input_file_path)
                transcribe(model=model, output_dir=output_dir, file=input_file_path, )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process audio files for transcription.')
    parser.add_argument('--path', default=".", help='path to audio file or directory', nargs='*')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser("~/Downloads/transcripts"),
                        help='Output directory for saving transcripts.')
    args = parser.parse_args()

    model = load_model()  # load model

    if os.path.isdir(args.path[0]):
        process_directory(args.path[0], args.output_dir, model)
    else:
        for path in args.path:
            transcribe(file=path, model=model, output_dir=args.output_dir)

import torch
from transformers import pipeline
from datasets import load_dataset
import torch

device = "cuda:0" if torch.cuda.is_available() else "cpu"

pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v2",
    chunk_length_s=30,
    device=device,
    return_timestamps=True,
    torch_dtype=torch.float16
)

pipe("10 x L2TS New 20 Dec 23/03 SEP 07183"
     " ID-1816 CALL NO-02 DR PATAM OUT GOING.mp3",
     generate_kwargs={"task": "translate", "language": "en", "repetition_penalty": 1.0}
     )

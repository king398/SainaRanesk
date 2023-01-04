import glob
from tqdm import tqdm
import whisper
import os

os.makedirs('transcripts_result', exist_ok=True)
model = whisper.load_model("models/large-v2.pt")
path = "/notebooks/AIML Datastes SR2.0"  # path to the audio files
files = glob.glob(f"{path}/*.mp3") + glob.glob(f"{path}/*/*.mp3")


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


def transcript_timestamp(transcript, text_file):
    for segment in transcript:
        text_file.write(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])} "
            f"Text: {segment['text'].strip().replace('-->', '->')}\n",
        )
    text_file.close()


for file in tqdm(files):
    result = model.transcribe(file, task='translate', verbose=True, no_speech_threshold=0.4,
                              condition_on_previous_text=False)
    text_file = open(f"transcripts_result/{file.split('/')[-1].split('.')[0]}.txt", "w")
    transcript_timestamp(result['segments'], text_file)

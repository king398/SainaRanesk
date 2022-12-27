from pydub import AudioSegment
from pydub.utils import make_chunks
import glob

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*.mp3") + glob.glob(
    "/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*/*.mp3")
print(len(files))

chunk_length_ms = 30000  # pydub calculates in millisec

for i in files:
    audio = AudioSegment.from_mp3(i)
    chunks = make_chunks(audio, chunk_length_ms)  # Make chunks of 30 sec
    for j, chunk in enumerate(chunks):
        chunk_name = i.split("/")[-1].split(".")[0] + "_{0}.mp3".format(j)
        print("exporting", chunk_name)
        chunk.export(f"/home/mithil/PycharmProjects/SainaRanesk/data/chunked_data/{chunk_name}", format="mp3")



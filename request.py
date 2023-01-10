import glob
import requests
from joblib import Parallel, delayed
import tqdm as tqdm

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*.mp3")[:40]


def request(file):
    r = requests.post('https://afc5-172-83-13-4.ngrok.io/transcribe', files={'file': open(file, 'rb')})
    print(r.json())


Parallel(n_jobs=20)(delayed(request)(file) for file in tqdm.tqdm(files))

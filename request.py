import glob
import requests
from joblib import Parallel, delayed
import tqdm as tqdm

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*.mp3")[:4]


def request(file):
    r = requests.post('http://192.168.0.126:5000/transcribe', files={
        'file': open(file, 'rb')})
    print(r.json())


Parallel(n_jobs=4)(delayed(request)(file) for file in tqdm.tqdm(files))

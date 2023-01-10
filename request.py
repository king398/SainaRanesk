import requests
import glob
from multiprocessing import Pool

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*.mp3")[:12]


def request(file):
    r = requests.post('https://758c-172-83-13-4.ngrok.io/transcribe', files={'file': open(f"{file}", 'rb')},
                      timeout=7200)
    print(r.json())


pool = Pool(4)  # number of users
pool.map(request, files)

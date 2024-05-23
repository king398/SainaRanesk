import requests
import glob
from multiprocessing import Pool

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/10 x L2TS New 20 Dec 23/*.mp3")[:6]


def request(file):
    r = requests.post('http://0.0.0.0:5000/transcribe', files={'file': open(f"{file}", 'rb')},
                      timeout=7200)
    print(r.json())


pool = Pool(4)  # number of users
pool.map(request, files)
file = files[0]
r = requests.post('http://0.0.0.0:5000/transcribe', files={'file': open(f"{file}", 'rb')},
                  timeout=7200)
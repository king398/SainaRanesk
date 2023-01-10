import glob
import requests
import multiprocessing

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*.mp3")[:20]


def request(file):
    r = requests.post('http://192.168.0.126:5000/transcribe', files={
        'file': open(file, 'rb')})
    print(r.json())


with multiprocessing.Pool(20) as p:
    p.map(request, files)

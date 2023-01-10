import glob
import requests
import multiprocessing

files = glob.glob("/home/mithil/PycharmProjects/SainaRanesk/data/AIML Datastes SR2.0/*.mp3")[:20]

r = requests.post('http://192.168.0.126:5000/transcribe', files={
    'file': open('/home/mithil/220714_2148.mp3', 'rb')})
print(r.json())


def request(file):
    r = requests.post('http://192.168.0.126:5000/transcribe', files={
        'file': open(file, 'rb')})
    print(r.json())


with multiprocessing.Pool(5) as p:
    p.map(request, files)

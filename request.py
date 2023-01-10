import requests

r = requests.post('http://192.168.0.126:5000/transcribe', files={
    'file': open('/home/mithil/220714_2148.mp3', 'rb')})
print(r.json())
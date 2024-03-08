import time
import requests

path = 'C:/Users/alanh/Downloads/librosa1.wav'

url = 'http://127.0.0.1:8000/translate/S2ST'
files = {'audio_file': (path.split('/')[-1], open(path, 'rb'), 'audio/wav')}
headers = {'accept': 'application/json'}


# # de esta forma se va poco a poco, reduciendo el tiempo de respuesta
# t = time.time()
# with requests.post(url, files=files) as r:
#     for chunk in r.iter_content(1024):
#         print('time: ', time.time()-t)

# # files['audio_file'][1].seek(0)


# de esta forma se obtiene completo
t = time.time()
response = requests.post(url, files=files)
print('time2: ', time.time()-t)
with open('test.wav', 'wb')  as file:
    file.write(response.content)
# print(response.content[0:1024])
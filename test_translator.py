import time
import requests
import pyaudio
import soundfile as sf
import io
import wave

#----------------------------Inicializar el stream de audio------------------------------------
CHUNK = 1024  # Tamaño del chunk
FORMAT = pyaudio.paFloat32  # Formato del audio (32 bits float)
CHANNELS = 1  # Número de canales (mono o estéreo)
RATE = 16000  # Frecuencia de muestreo

p_audio = pyaudio.PyAudio()
out_stream = p_audio.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

in_stream = p_audio.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
#----------------------------------------------------------------

path = 'C:/Users/alanh/Downloads/librosa1.wav'

url = 'http://127.0.0.1:8000/translate/S2ST'
# url = 'https://ec2-18-119-115-208.us-east-2.compute.amazonaws.com/'
files = {'audio_file': (path.split('/')[-1], open(path, 'rb'), 'audio/wav')}
headers = {'accept': 'application/json'}


# de esta forma se va poco a poco, reduciendo el tiempo de respuesta
t = time.time()

while True:
    frames = []
    for i in range(0, int(RATE / CHUNK * 1)):
        data = in_stream.read(CHUNK)
        frames.append(data)
    # b_audio = in_stream.read(CHUNK)
    b_audio = b''.join(frames)
    with io.BytesIO(b_audio) as bytes_io:
        with wave.open(bytes_io, 'wb') as wave_file:
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(p_audio.get_sample_size(FORMAT))
            wave_file.setframerate(RATE)
            wave_file.writeframes(b_audio)
            
        # Rebobinar el archivo WAV
        bytes_io.seek(0)

        # Crear un archivo temporal WAV
        files = {'audio_file': (path.split('/')[-1], bytes_io, 'audio/wav')}
        
        # Enviar el archivo WAV a la API
        with requests.post(url, files=files) as r:
            for chunk in r.iter_content(1024):
                out_stream.write(chunk)
                
        
out_stream.stop_stream()
out_stream.close()
p_audio.terminate()

# files['audio_file'][1].seek(0)


# de esta forma se obtiene completo
# t = time.time()
# response = requests.post(url, files=files, verify=False)
# print('time2: ', time.time()-t)
# print(response.headers)
# with open('test.wav', 'wb')  as file:
#     file.write(response.content)
# print(response.content[0:1024])
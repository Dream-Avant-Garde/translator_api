import requests
import pyaudio
import wave
import io

#----------------------------Parámetros de la grabación------------------------------------
CHUNK = 1024  # Tamaño del chunk
FORMAT = pyaudio.paInt16  # Formato del audio (16 bits)
CHANNELS = 1  # Número de canales (mono)
RATE = 16000  # Frecuencia de muestreo
RECORD_SECONDS = 3  # Duración de la grabación en segundos
WAVE_OUTPUT_FILENAME = "input.wav"
TGT_LANG = 'eng'

# Inicializar PyAudio
p = pyaudio.PyAudio()

#-----------------------------Abrir un stream de audio-----------------------------------
stream_in = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

stream_out = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

print("* Grabando...")

frames = []

#-----------------------------Capturar audio durante RECORD_SECONDS segundos----------------
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream_in.read(CHUNK)
    frames.append(data)

print("* Grabación terminada")

# Detener y cerrar el stream de audio
stream_in.stop_stream()
stream_in.close()


#-----------------------------Grabar audio en stream en un archivo en memoria-----------------------------------

input_buffer = io.BytesIO()
wf = wave.open(input_buffer, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

input_buffer.seek(0)  # Regresar al inicio del buffer


# # guardar archivo
# wf = wave.open('input.wav', 'wb')
# wf.setnchannels(CHANNELS)
# wf.setsampwidth(p.get_sample_size(FORMAT))
# wf.setframerate(RATE)
# wf.writeframes(input_buffer.read())
# wf.close()

#-------------------------Hacer la request---------------------------------------
url = f'http://54.233.162.242:80/translate/S2ST/'    
# url = f'http://localhost:8000/translate/S2ST'    
# settings = {"tgt_lang": "eng", "description": "Spanish translation", "chuck_size": 1024}
headers = {'accept': 'application/json'}
files = {'audio_file': ('input.wav', input_buffer)}

# con stream response
with requests.post(url, files=files, verify=False) as response:
    for chunk in response.iter_content(CHUNK):
        stream_out.write(chunk)

stream_out.stop_stream()
stream_out.close()

# sin stream response
# response = requests.post(url, files=files, verify=False)
# with open('output.wav', 'wb') as ouput_buffer:
#     ouput_buffer.write(response.content)


# cerrar archivo
input_buffer.close()

#TERMINAR pyaudio
p.terminate()


import asyncio
import websockets
import pyaudio
import wave
import io
import time
import contextlib

from enum import Enum

class Tgt_Languaje(Enum):
    spa = "spa"
    eng = "eng"
    fra = "fr"

#----------------------------Parámetros de la grabación------------------------------------
CHUNK = 1024  # Tamaño del chunk
FORMAT = pyaudio.paInt16  # Formato del audio (16 bits)
CHANNELS = 2  # Número de canales (mono)
RATE = 48000  # Frecuencia de muestreo
N_FRAMES = 0
SAMP_WIDTH = 0
WAVE_INPUT_FILENAME = "test/in_audios/testaudio48.wav"
WAVE_OUTPUT_FILENAME = WAVE_INPUT_FILENAME.replace('in_audios', 'out_audios')

# Inicializar PyAudio
p = pyaudio.PyAudio()

#-----------------------------Abrir un stream de audio-----------------------------------
stream_out = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

def get_bytes(path: str):
    with open(path, 'rb') as f: 
        return f.read()

def update_wav_headers(path):
    global CHANNELS, FORMAT, RATE, N_FRAMES, SAMP_WIDTH
    with contextlib.closing(wave.open(path, 'rb')) as f:
        params = f.getparams()
        CHANNELS = params.nchannels
        RATE = params.framerate
        N_FRAMES = params.nframes
        SAMP_WIDTH = params.sampwidth
        if params.sampwidth == 1: 
            FORMAT = pyaudio.paInt8
        elif params.sampwidth == 2:
            FORMAT = pyaudio.paInt16
        elif params.sampwidth == 4:
            FORMAT = pyaudio.paInt32
update_wav_headers('test/in_audios/testaudio48.wav')
async def connect_and_chat():
    ws = await websockets.connect("wss://54.233.162.242:80/translate/ws/S2ST/", ssl=False)
    try:
        # send settings
        settings = {"tgt_lang": Tgt_Languaje.eng}
        await ws.send(str(settings))
        response = await ws.recv()

        t1 = time.time()
        print('se envian los datos al server')
        print('longitud del IN audio: ', N_FRAMES / RATE)
        await ws.send(get_bytes(WAVE_INPUT_FILENAME))
        response = await ws.recv()
        print('Tiempo de respuesta: ', time.time() - t1, ' seconds')
        print('longitud de la respuesta: ', len(response))
        print('longitud del OUT audio: ', len(response) / (RATE * SAMP_WIDTH))
        with open(WAVE_OUTPUT_FILENAME, 'wb') as f: 
            f.write(response)
            print('Audio output saved on: ', WAVE_OUTPUT_FILENAME)

        await ws.close() 
    except asyncio.TimeoutError:
        print("Connection timed out.")
    except websockets.ConnectionClosed as e:
        print("Connection closed:", e)
    except Exception as e: 
        print("Error:", e)

# Ejemplo de uso
asyncio.run(connect_and_chat())
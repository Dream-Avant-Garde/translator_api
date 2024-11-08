import asyncio
import websockets
import pyaudio
import wave
import io
import numpy as np

#----------------------------Parámetros de la grabación------------------------------------
CHUNK = 1024  # Tamaño del chunk
FORMAT = pyaudio.paInt32  # Formato del audio (16 bits)
CHANNELS = 1  # Número de canales (mono)
RATE = 16000  # Frecuencia de muestreo
RECORD_SECONDS = 4  # Duración de la grabación en segundos
WAVE_OUTPUT_FILENAME = "test/in_audios/testaudio48.wav"

# Inicializar PyAudio
p = pyaudio.PyAudio()

#-----------------------------Abrir un stream de audio-----------------------------------
stream_in = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True)

stream_out = p.open(
    format=pyaudio.paInt32,          # Formato de 32 bits en flotante
    channels=1,                        # Mono
    rate=16000,                  # Frecuencia de muestreo (16000 Hz)
    output=True
)

input('Enter para empezar...')
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

input_buffer.seek(0)


async def connect_and_chat():
    ws = await websockets.connect("wss://52.14.194.163:80/translate/ws/S2ST/", ssl=False)
    try:
        await ws.send(input_buffer.read())

        response = await ws.recv()
        with open('test/out_audios/out_audio.wav', 'wb') as file:
            file.write(response)
        response = response[44:]

        stream_out.write(response)

        await ws.close()
        
    except Exception as e:
        print("Error:", e)

# Ejemplo de uso
asyncio.run(connect_and_chat())


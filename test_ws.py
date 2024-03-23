import asyncio
import websockets
import pyaudio
import wave
import io

#----------------------------Parámetros de la grabación------------------------------------
CHUNK = 1024  # Tamaño del chunk
FORMAT = pyaudio.paInt16  # Formato del audio (16 bits)
CHANNELS = 1  # Número de canales (mono)
RATE = 16000  # Frecuencia de muestreo
RECORD_SECONDS = 6  # Duración de la grabación en segundos
WAVE_OUTPUT_FILENAME = "input.wav"

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


# async def connect_and_chat():
#     async with websockets.connect("ws://localhost:8000/ws") as websocket:
#         message = open("C:/Users/alanh/Downloads/librosa1.wav", 'rb').read()
#         await websocket.send(message)

#         i = 0
#         try:
#             while True:
#                 response = await websocket.recv()
#                 i += 1

#                 if len(response) == 1024:
#                     print(f'response{i}:', len(response))
#                     print('--------------------------------')
#                 else:
#                     print(f'response{i}:', len(response))
#                     break 

#             await websocket.close() 
#         except asyncio.TimeoutError:
#             print("Connection timed out.")
#         except websockets.ConnectionClosed as e:
#             print("Connection closed:", e)
#         except Exception as e:  # Catch other potential exceptions
#             print("Error:", e)

# asyncio.run(connect_and_chat())


async def connect_and_chat():
    ws = await websockets.connect("wss://3.144.138.81:80/ws/", ssl=False    )
    try:
        # ... su código usando `ws` ...

        # Ejemplo: Enviando datos
        # with open("C:/Users/alanh/Downloads/librosa1.wav", 'rb') as audio_file:
        #     await ws.send(audio_file.read())
        await ws.send(input_buffer.read())

        # Ejemplo: Recibiendo datos
        i = 0
        try:
            while True:
                response = await ws.recv()
                i += 1

                stream_out.write(response)
                if len(response) == 1024:
                    print(f'response{i}:', len(response))
                    print('--------------------------------')
                else:
                    print(f'response{i}:', len(response))
                    break 
            await ws.close() 
        except asyncio.TimeoutError:
            print("Connection timed out.")
        except websockets.ConnectionClosed as e:
            print("Connection closed:", e)
        except Exception as e:  # Catch other potential exceptions
            print("Error:", e)
        # ... otras operaciones usando `ws` ...
    except Exception as e:
        print("Error:", e)

# Ejemplo de uso
asyncio.run(connect_and_chat())


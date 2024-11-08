import asyncio
import websockets
import io

async def send_audio_and_receive_translation():
    # Dirección del servidor WebSocket
    uri = "ws://52.14.194.163:80/stream/ws/S2ST/"

    async with websockets.connect(uri) as websocket:
        print("Conexión establecida con el WebSocket")

        # Abre el archivo de audio y lee su contenido en bytes
        with open("test/in_audios/input.wav", "rb") as audio_file:
            audio_data = audio_file.read()

        # Envía el audio en fragmentos al servidor
        chunk_size = 320  # Tamaño del segmento en bytes, puedes ajustarlo según necesites
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            await websocket.send(chunk)
            print(f"Enviado chunk de tamaño {len(chunk)} bytes")

            # Espera la respuesta de traducción
            response = await websocket.recv()
            
            if isinstance(response, bytes):
                # Asume que es audio si recibes bytes
                with open("translated_audio.wav", "ab") as output_audio:
                    output_audio.write(response)
                print("Recibido segmento de audio traducido")
            else:
                # Asume que es texto si recibes un string
                print("Recibido texto traducido:", response)

        print("Audio completo enviado")

        # Finaliza la conexión
        await websocket.close()
        print("Conexión WebSocket cerrada")

# Ejecuta el cliente WebSocket
asyncio.run(send_audio_and_receive_translation())

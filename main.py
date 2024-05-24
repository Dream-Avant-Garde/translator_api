from dependencies import *

from routers import translator, ex_translator, ws_translator

from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, Response
import asyncio


app = FastAPI()
app.include_router(translator.router)
app.include_router(ws_translator.router)
app.include_router(ex_translator.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)

@app.middleware('http')
async def validate_ip(request: Request, call_next):
    # Get client IP
    ip = str(request.client.host)
    
    # Check if IP is allowed
    if ip not in WHITELISTED_IPS:
        data = {
            'message': f'IP {ip} is not allowed to access this resource.'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Proceed if IP is allowed
    return await call_next(request)


@app.get('/')
async def home():
    return 'Welcome to Translator API'


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=100)
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break
            
            with open('data.wav', 'wb') as f:
                f.write(data)

            for i in range(0, len(data), 1024):
                await websocket.send_bytes(data[i:i + 1024])
            

    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print("Error inesperado:", e)


@app.websocket("/S2ST/")
async def speech_to_speech_translation(websocket: WebSocket):
    try:
        tgt_lang = 'eng'
        await websocket.accept()
        
        b_data = io.BytesIO()

        while True:
            tgt_lang = await websocket.receive_text()
            if tgt_lang in ('eng', 'spa', 'fra', 'deu', 'ita', 'hin', 'cmn'):
                break

        print('Target lang: ', tgt_lang)
        while True:
            try:
                bytes_data = await websocket.receive_bytes()
                
                b_data.write(bytes_data)
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break

            b_data.seek(0)

            # preprocess data
            data, sampling_rate = torchaudio.load(uri=b_data)
            data = torchaudio.functional.resample(data, orig_freq=sampling_rate, new_freq=16000)

            # make inference
            output = seamlees_m4t.s2st(tgt_lang, data.transpose(0,1))
            out_audio = torchaudio.functional.resample(output[1].audio_wavs[0][0].to(torch.float32).cpu(), orig_freq=16000, new_freq=sampling_rate)
            print('Text output: ', output[0])

            # restart buffer
            b_data.seek(0)
            b_data.truncate(0)
            b_data.flush()  

            # load audio on buffer
            torchaudio.save(uri=b_data, src=out_audio, sample_rate=sampling_rate, format='wav', buffer_size=1024, bits_per_sample=32)

            # go to index byte 0
            b_data.seek(0)

            # return bytes audio
            await websocket.send_bytes(b_data.read())

            # restart buffer
            b_data.seek(0)
            b_data.truncate(0)
            b_data.flush()  

    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print("Error inesperado:", e)


# uvicorn main:app --reload
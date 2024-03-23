from dependencies import *

from routers import translator, ex_translator, ws_translator

from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse
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
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=10)
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break

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
            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=10)
                
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break
            for i in range(0, len(data), len(data)):
                wf = wave.open(b_data, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(4)
                wf.setframerate(16000)
                wf.writeframes(data[i:i + 1024])
                wf.close()
                b_data.seek(0)
                
                data, sampling_rate = torchaudio.load(b_data)
                data = data.transpose(0,1)
                output = seamlees_m4t.s2st(tgt_lang,data)
                text, speech = output
                b_data.seek(0)
                b_data.truncate(0)
                b_data.flush()

                torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), speech.sample_rate, format='wav')
                
                b_data.seek(44)
                await websocket.send_bytes(b_data.read())

                b_data.seek(0)
                b_data.truncate(0)
                b_data.flush()
    except WebSocketDisconnect:
        print("Cliente desconectado.")
    # except Exception as e:
    #     print("Error inesperado:", e)

# uvicorn main:app --reload
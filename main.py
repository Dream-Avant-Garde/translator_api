from dependencies import *

# from routers import translator, ex_translator, ws_translator

from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, Response, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

import io
import asyncio
import os


app = FastAPI()
# app.include_router(translator.router)
# app.include_router(ws_translator.router)
# app.include_router(ex_translator.router)

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        print('Request')
        print('headers: ', request.headers)
        print('body: ', await request.body())
        print('orm: ', await request.form())
        print('method: ', request.method)
        print('--------------------------------')
        print('EXC')
        print('exc: ', exc)

        
    except Exception as e:
        print('Error: request: ', e)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post('/S2ST', tags=['translate'])
async def speech_to_speech_ranslation(audio_file: UploadFile = File(...)):
    byte_data = await audio_file.read()

    b_data = io.BytesIO(byte_data)
    print(b_data.getvalue()[0:100])

    return Response(b_data.getvalue(), media_type='audio/wav')
    # return StreamingResponse(return_streaming_audio(b_data.getvalue()), media_type='audio/wav')

socket_clients = []
i = 0
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global i
    try:
        await websocket.accept()
        socket_clients.append(websocket)
        
        while True:
            try:
                data = await websocket.receive_bytes()
                print('Entrada# ', i)
                print('len data:', len(data))
                print('byte data: ', data[0:44])
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break
            
            if os.path.exists('audios/'):
                with open(f'audios/{i}.wav', 'wb') as file:
                    file.write(data)
                    i += 1
            else: os.mkdir('audios/')

            b_data = io.BytesIO(data)

            data, sampling_rate = torchaudio.load(b_data)
            sampling_rate = 16000
            data = data.transpose(0,1)
            output = seamlees_m4t.s2st('eng',data)
            b_data = io.BytesIO()
            torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), sampling_rate, format='wav')
            print('sample rate: ', sampling_rate)

            if os.path.exists('audios/'):
                with open(f'audios/out{i-1}.wav', 'wb') as file:
                    file.write(b_data.getvalue())

            print('Respuesta enviada')
            print('\n----------------------------------------------------------------\n')
            await websocket.send_bytes(b_data.getvalue())


    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print("Error inesperado:", e)

# uvicorn main:app --reload
from dependencies import *

from routers import translator, ex_translator, ws_translator

from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
import asyncio
import json


app = FastAPI()
app.include_router(translator.router)
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
        print(str(request.items()))
        print(exc.args)
        print(exc.errors())
        print(exc.body)
        
    except Exception as e:
        print('Error: request: ', e)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.post("/json")
async def receive_json(request: Request):
    # Read the JSON data from the request body
    try:
        json_data = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON data"}, status_code=400)

    # Process the JSON data
    print(f"Received JSON data: {json_data}")
    # You can perform any processing or validation logic here based on the JSON data

    # Prepare a response
    response_data = {
        "message": "JSON data received and processed successfully",
        "data": json_data
    }

    return JSONResponse(response_data)


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
            
            # with open('data.wav', 'wb') as f:
            #     f.write(data)
            await websocket.send_bytes(data)
            # for i in range(0, len(data), 1024):
            #     await websocket.send_bytes(data[i:i + 1024])
            

    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print("Error inesperado:", e)

@app.post('/S2ST', tags=['translate'])
async def speech_to_speech_ranslation(audio_file):

    print(audio_file)

    return audio_file



# uvicorn main:app --reload
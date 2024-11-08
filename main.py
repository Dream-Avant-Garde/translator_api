from fastapi import FastAPI, Request, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dependencies import *
from routers import translator, ex_translator, ws_translator, stream

app = FastAPI()

# Incluir los routers
# app.include_router(translator.router)
# app.include_router(ws_translator.router)
# app.include_router(ex_translator.router)
app.include_router(stream.router)

# Middleware para CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)

@app.middleware('http')
async def validate_ip(request: Request, call_next):
    ip = str(request.client.host)
    if ip not in WHITELISTED_IPS:
        data = {'message': f'IP {ip} is not allowed to access this resource.'}
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
    return await call_next(request)

@app.get('/')
async def home():
    return 'Welcome to Translator API'

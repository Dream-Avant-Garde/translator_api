###########################Python####################################
from typing import Annotated
from fastapi import Request, status
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware



import uvicorn

import torch
import torchaudio
import io
import wave
from src.model import seamlees_m4t 

###########################Local#####################################
    
from src.func import get_valid_ips


origins = [ # acepts all domains
    '*',
] 
methods = [ # acepts all methods
    '*',
]
headers = [ # acepts all headers
    '*',
]

WHITELISTED_IPS = get_valid_ips()


#WEBSOCKET CLIENTS
socket_clients = dict()
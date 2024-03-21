from fastapi import APIRouter, Request, File, UploadFile, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.responses import StreamingResponse
from .models import TranslateSettings
from typing import Optional
import torchaudio
import asyncio
import torch
import io
# local
from src.func import return_streaming_audio
from src.model import seamlees_m4t 

def get_default_settings():
    return TranslateSettings(
        tgt_lang='eng',
        chuck_size=1024
    )

router = APIRouter(
    prefix='/translate'
)

@router.get('/', tags=['translate'])
async def traslate():
    return 'test'

@router.post('/S2ST', tags=['translate'])
async def speech_to_speech_ranslation(audio_file: UploadFile = File(...), settings: Optional[TranslateSettings] = Depends(get_default_settings)):
    byte_data = await audio_file.read()
    print('entra')
    b_data = io.BytesIO(byte_data)

    data, sampling_rate = torchaudio.load(b_data)
    data = data.transpose(0,1)
    output = seamlees_m4t.s2st(settings.tgt_lang,data)
    text, speech = output
    b_data = io.BytesIO()
    torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), speech.sample_rate, format='wav')


    return StreamingResponse(return_streaming_audio(b_data.getvalue()), media_type='audio/wav')

@router.websocket("/ws/S2ST/{tgt_lang}", name='translate')
async def speech_to_speech_translation(websocket: WebSocket, tgt_lang:str):
    try:
        await websocket.accept()
        
        while True:
            try:
                byte_data = await asyncio.wait_for(websocket.receive_bytes(), timeout=1000)
                with open('data.wav','wb') as f:
                    f.write(byte_data)
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break
            
            for i in range(0, len(byte_data), 1024):
                b_data = io.BytesIO(byte_data[i:i + 1024])
                data, sampling_rate = torchaudio.load(b_data)
                data = data.transpose(0,1)
                output = seamlees_m4t.s2st(tgt_lang,data)
                text, speech = output
                b_data = io.BytesIO()
                torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), speech.sample_rate, format='wav')
                await websocket.send_bytes(byte_data)
            
    except WebSocketDisconnect:
        print("WebSocket disconnected")


from fastapi import APIRouter, Request, File, UploadFile, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.responses import StreamingResponse

from typing import Optional
import torchaudio
import asyncio
import torch
import io
import wave
# local
from src.func import return_streaming_audio
from .models import TranslateSettings
from src.model import seamlees_m4t 

def get_default_settings():
    return TranslateSettings(
        tgt_lang='eng',
        description='default',
        chuck_size=1024
    )

router = APIRouter(
    prefix='/translate'
)

@router.get('/', tags=['translate'])
async def traslate():
    return 'test'

@router.post('/S2ST', tags=['translate'])
async def speech_to_speech_ranslation(audio_file: UploadFile = File(...)):
    byte_data = await audio_file.read()
    print('entra')
    b_data = io.BytesIO(byte_data)
    settings = get_default_settings()

    data, sampling_rate = torchaudio.load(b_data)
    data = data.transpose(0,1)
    output = seamlees_m4t.s2st(settings.tgt_lang,data)
    b_data = io.BytesIO()
    torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), sampling_rate, format='wav')


    return StreamingResponse(return_streaming_audio(b_data.getvalue()), media_type='audio/wav')

@router.websocket("/ws/S2ST/", name='translate')
async def speech_to_speech_translation(websocket: WebSocket):
    try:
        tgt_lang = 'eng'
        await websocket.accept()
        
        b_data = io.BytesIO()
            
        
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

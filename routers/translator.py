from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import torchaudio
import asyncio
import torch
import io
import wave

from src.func import return_streaming_audio
from .models import TranslateSettings
from src.model import seamlees_m4t 

router = APIRouter(prefix='/translate')

def get_default_settings():
    return TranslateSettings(
        tgt_lang='eng',
        description='default',
        chuck_size=1024
    )

@router.get('/', tags=['translate'])
async def translate():
    return 'test'

@router.post('/S2ST', tags=['translate'])
async def speech_to_speech_translation(audio_file: UploadFile = File(...)):
    byte_data = await audio_file.read()
    b_data = io.BytesIO(byte_data)
    settings = get_default_settings()

    data, sampling_rate = torchaudio.load(b_data)
    data = data.transpose(0, 1)
    output = seamlees_m4t.s2st(settings.tgt_lang, data)
    b_data = io.BytesIO()
    torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), sampling_rate, format='wav')

    return StreamingResponse(return_streaming_audio(b_data.getvalue()), media_type='audio/wav')

@router.websocket("/ws/S2ST/{tgt_lang}")
async def speech_to_speech_translation(websocket: WebSocket, tgt_lang: str):
    try:
        await websocket.accept()
        b_data = io.BytesIO()
        while True:
            try:
                bytes_data = await asyncio.wait_for(websocket.receive_bytes(), timeout=10)
                b_data.write(bytes_data)
                b_data.seek(0)

                data, sampling_rate = torchaudio.load(b_data)
                data = torchaudio.functional.resample(data, orig_freq=sampling_rate, new_freq=16000)

                output = seamlees_m4t.s2st(tgt_lang, data.transpose(0, 1))
                out_audio = torchaudio.functional.resample(output[1].audio_wavs[0][0].to(torch.float32).cpu(), orig_freq=16000, new_freq=sampling_rate)

                b_data.seek(0)
                b_data.truncate(0)

                torchaudio.save(b_data, out_audio, sample_rate=sampling_rate, format='wav')

                b_data.seek(0)
                await websocket.send_bytes(b_data.read())
                b_data.truncate(0)
            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break
    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print("Error inesperado:", e)

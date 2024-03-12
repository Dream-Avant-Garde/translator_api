from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import StreamingResponse
import librosa
import io
# local
from src.func import return_streaming_audio
from src.model.seamlees_m4t import *

router = APIRouter(
    prefix='/ws_translate'
)


@router.get('/', tags=['ws_translate'])
async def ws_translate():
    return 'test'

@router.post('/S2ST', tags=['ws_translate'])
async def speech_to_speech_translation(request: Request, audio_file: UploadFile = File(...)):
    byte_data = await audio_file.read()

    b_data = io.BytesIO(byte_data)  # No necesitas llamar a .read() de nuevo
    data, sampling_rate = librosa.load(b_data)

    return StreamingResponse(return_streaming_audio(byte_data), media_type='audio/wav')

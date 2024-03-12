from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import StreamingResponse
import torchaudio
import io
# local
from src.func import return_streaming_audio
# from src.model import seamlees_m4t 


router = APIRouter(
    prefix='/translate'
)

@router.get('/', tags=['translate'])
async def traslate():
    return 'test'

@router.post('/S2ST', tags=['translate'])
async def speech_to_speech_ranslation(request: Request, audio_file: UploadFile = File(...)):
    byte_data = await audio_file.read()

    b_data = io.BytesIO(byte_data)
    # data, sampling_rate = torchaudio.load(b_data, format='wav')
    # data = data.transpose(0,1)
    # output = seamlees_m4t.s2st('spa', data)
    # b_data = io.BytesIO()
    # # torchaudio.save(b_data, output[1].audio_wavs[0][0].to(torch.float32).cpu(), output[1].sample_rate, format='wav')
    # torchaudio.save(b_data, output[1][0], output[1][1], format='wav')


    return StreamingResponse(return_streaming_audio(b_data.getvalue()), media_type='audio/wav')

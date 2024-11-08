from seamless_communication.streaming.agents.seamless_streaming_s2st import (
    SeamlessStreamingS2STJointVADAgent,
)
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import io
from src.audio import *
import torch
import torchaudio


router = APIRouter(prefix='/translate')


print("building system from dir")
agent_class = SeamlessStreamingS2STJointVADAgent
tgt_lang = "spa"

model_configs = dict(
    source_segment_size=320,
    device="cuda:0",
    dtype="fp16",
    min_starting_wait_w2vbert=192,
    decision_threshold=0.5,
    min_unit_chunk_size=50,
    no_early_stop=True,
    max_len_a=0,
    max_len_b=100,
    task="s2st",
    tgt_lang=tgt_lang,
    block_ngrams=True,
    detokenize_only=True,
)
system = build_streaming_system(model_configs, agent_class)
system_states = system.build_states()
print("finished building system")

@router.websocket("/ws/S2ST/", name='stream')
async def speech_to_speech_translation(websocket: WebSocket):
    try:
        await websocket.accept()

        tgt_lang = 'eng'
        source_segment_size = 320
        b_data = io.BytesIO()

        while True:
            try:
                baudio = await websocket.receive_bytes()
                
                with open(f'/home/ubuntu/translator_api/audios/input_audio.wav', 'wb') as file:
                    file.write(baudio)

            except asyncio.TimeoutError:
                print("La conexión se ha agotado.")
                break

            audio_frontend = AudioFrontEnd(
                wav_data=audio,
                segment_size=source_segment_size,
            )

            while True:
                input_segment = audio_frontend.send_segment()
                input_segment.tgt_lang = tgt_lang

                if input_segment.finished:
                    get_states_root(system, system_states).source_finished = True
                output_segments = OutputSegments(system.pushpop(input_segment, system_states))

                if not output_segments.is_empty:
                    for segment in output_segments.segments:
                        if isinstance(segment, SpeechSegment):
                            audio_tensor = torch.tensor(segment.content, dtype=torch.float32).unsqueeze(0)
                            torchaudio.save(f"/content/output/{i}output.wav", audio_tensor, 16000)
                            websocket.send_bytes()
                        elif isinstance(segment, TextSegment):
                            print(segment.content)
                if output_segments.finished:
                    print("End of VAD segment")
                    reset_states(system, system_states)
                if input_segment.finished:
                    assert output_segments.finished
                    break
            
            

    except WebSocketDisconnect:
        print("Cliente desconectado.")
    except Exception as e:
        print("Error inesperado:", e)
import io
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import mmap
import numpy
import soundfile
import torchaudio
import torch
import librosa
from config.config import seamless_config

from collections import defaultdict
from pathlib import Path
from pydub import AudioSegment

from seamless_communication.inference import Translator
from seamless_communication.streaming.dataloaders.s2tt import SileroVADSilenceRemover


model_name = seamless_config['model']
vocoder_name = seamless_config['vocoder'][0] if model_name == "seamlessM4T_v2_large" else seamless_config['vocoder'][1]
device = seamless_config['device']
    
translator = Translator(
    model_name,
    vocoder_name,
    device=torch.device(device),
    # device=torch.device("cpu"),
    dtype=torch.float16,
)

def s2st(tgt_lang:str, data:torch.Tensor):
    output = translator.predict(
        input=data,
        task_str=seamless_config['task'],
        tgt_lang=tgt_lang,
    )
    return output
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
import yaml

from collections import defaultdict
from pathlib import Path
from pydub import AudioSegment

from seamless_communication.inference import Translator
from seamless_communication.streaming.dataloaders.s2tt import SileroVADSilenceRemover

with open ('config/seamless_m4t.yml', 'r') as seamless_m4t_ymlfile:
    seamless_config = yaml.safe_load(seamless_m4t_ymlfile)

def translator_config():
    model_name = seamless_config['model']
    vocoder_name = seamless_config['vocoder'][0] if model_name == "seamlessM4T_v2_large" else seamless_config['vocoder'][1]

    translator = Translator(
        model_name,
        vocoder_name,
        device=torch.device("cuda:0"),
        # device=torch.device("cpu"),
        dtype=torch.float16,
    )
    return translator

def s2st(tgt_lang:str, data:torch.Tensor):
    translator = translator_config()
    output = translator.predict(
        input=data,
        task_str=seamless_config['task'],
        tgt_lang=tgt_lang,
    )
    return output
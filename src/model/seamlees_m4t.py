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

from collections import defaultdict
from pathlib import Path
from pydub import AudioSegment

from seamless_communication.inference import Translator
from seamless_communication.streaming.dataloaders.s2tt import SileroVADSilenceRemover

text_example = 'El examen y testimonio de los expertos permitieron a la comisión concluir que cinco disparos pueden haber sido disparados.'

model_name = "seamlessM4T_v2_large"
vocoder_name = "vocoder_v2" if model_name == "seamlessM4T_v2_large" else "vocoder_36langs"

translator = Translator(
    model_name,
    vocoder_name,
    device=torch.device("cuda:0"),
    # device=torch.device("cpu"),
    dtype=torch.float16,
)

def s2st(tgt_lang:str, data:torch.Tensor, samplerate=16000):
  output = translator.predict(
      input=data,
      task_str="s2st",
      tgt_lang=tgt_lang,
      sample_rate=samplerate
  )
  return output
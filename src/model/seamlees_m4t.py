import torch
import torchaudio

text_example = 'El examen y testimonio de los expertos permitieron a la comisión concluir que cinco disparos pueden haber sido disparados.'


def s2st(tgt_lang:str, data:torch.Tensor):
#   output = translator.predict(
#       input=data,
#       task_str="s2st",
#       tgt_lang=tgt_lang,
#   )
  audio_tensor = torch.load('D:/Trabajo/translator_api/audio.pt')
  output = (text_example, (audio_tensor, 16000))
  return output
from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel

class TranslateSettings(BaseModel):
    tgt_lang: str = 'eng'
    description: Optional[str] = None
    chuck_size: int = 1024
from typing import Union, Optional
from pydantic import BaseModel

class TranslateSettings(BaseModel):
    tgt_lang: str = 'eng'
    description: Optional[str] = None
    chuck_size: int = 1024
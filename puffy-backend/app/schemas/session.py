from app.schemas.base import BaseModel
from enum import Enum
from pydantic import Field
from typing import List, Optional
import decimal


class SessionInfo(BaseModel):
    session_id: str
    message: Optional[str] = None

    class Config:
        exclude_none = True

class SessionData(BaseModel):
    message: str
    email: Optional[str] = None

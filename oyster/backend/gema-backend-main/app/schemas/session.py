from app.schemas.base import BaseModel
from typing import Optional


class SessionInfo(BaseModel):
    session_id: str
    message: Optional[str] = None

    class Config:
        exclude_none = True

class SessionData(BaseModel):
    message: str
    email: Optional[str] = None

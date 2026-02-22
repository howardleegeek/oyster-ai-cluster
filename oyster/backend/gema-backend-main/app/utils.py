from .config import Settings, get_settings
from fastapi import Depends
from pydantic import BaseModel
from app.plib import *
from app.ext_service import *
from typing_extensions import Annotated


def get_sol():
    settings = get_settings()
    return SolWrapper(key=settings.sol_key)


SettingsDep = Annotated[Settings, Depends(get_settings)]
SolDep = Annotated[SolWrapper, Depends(get_sol)]


settings = get_settings()



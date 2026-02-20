from .config import Settings, get_settings
from .error import UserError, ServerError
from fastapi import FastAPI, Depends, Request, HTTPException
from pydantic import BaseModel
from app.plib import *
from app.ext_service import *
from typing_extensions import Annotated
from sqlalchemy.orm import Session

from typing import Union, Optional, List
import decimal
import logging
import logging.handlers
from contextlib import contextmanager
from fastapi.middleware.cors import CORSMiddleware
import time
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from enum import Enum


def get_tg_service():
    settings = get_settings()
    return TgService(settings.tg_bot_token)


def get_sol():
    settings = get_settings()
    return SolWrapper(key=settings.sol_key)


SettingsDep = Annotated[Settings, Depends(get_settings)]
TgServiceDep = Annotated[TgService, Depends(get_tg_service)]
SolDep = Annotated[SolWrapper, Depends(get_sol)]


settings = get_settings()


class SuccessResp(BaseModel):
    status: str = "success"


from fastapi import FastAPI
import logging
import logging.handlers
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .config import get_settings
from app.api.user import router as user_router
from app.api.product import router as product_router
from app.db.base import Base, engine


def start_app():
    app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False}, openapi_url="/apidoc/openapi.json")
    app.include_router(user_router)
    app.include_router(product_router)
    settings = get_settings()
    if settings.env == "DEV":
        origins = ["*"]  # Replace "*" with specific origins if needed
        app.add_middleware(
            CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
        )
    Base.metadata.create_all(bind=engine)
    return app


app = start_app()
load_dotenv()


def get_logger(n):
    pid = os.getpid()
    alogger = logging.getLogger(n)
    alogger.setLevel(logging.DEBUG)
    fhandler = logging.handlers.RotatingFileHandler(
        f'logs/{n}-{pid}.log', mode='a', encoding='utf-8', maxBytes=6000000, backupCount=2)
    fmt = logging.Formatter(
        '{asctime} {process} {filename}:{lineno} {name} {levelname:8s} {message}', style='{')
    fhandler.setFormatter(fmt)
    alogger.addHandler(fhandler)
    shandler = logging.StreamHandler()
    shandler.setFormatter(fmt)
    alogger.addHandler(shandler)
    return alogger


logger = get_logger('__main__')

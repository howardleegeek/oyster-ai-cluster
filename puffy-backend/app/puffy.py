from app.api.user import router as user_router
from app.api.product import router as product_router
from app.api.order import router as order_router
from app.config import get_settings
from app.db.base import Base, engine, get_db
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import logging
import logging.handlers
import os


def start_app():
    app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False}, openapi_url="/apidoc/openapi.json")
    app.include_router(user_router)
    app.include_router(product_router)
    app.include_router(order_router)
    settings = get_settings()
    if settings.env == "DEV":
        origins = ["*"]  # Replace "*" with specific origins if needed
        app.add_middleware(
            CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
        )
    Base.metadata.create_all(bind=engine)
    return app


puffy = start_app()
load_dotenv()


@puffy.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@puffy.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


def setup_logging():
    pid = os.getpid()
    file_name = f"logs/oysrepublic{pid}.log"
    fhandler = logging.handlers.RotatingFileHandler(
        f'logs/oysrepublic.log', mode='a', encoding='utf-8', maxBytes=6000000, backupCount=2)
    fmt = logging.Formatter(
        '{asctime} {thread} {filename}:{lineno} {name} {levelname:8s} {message}', style='{')
    fhandler.setFormatter(fmt)
    shandler = logging.StreamHandler()
    shandler.setFormatter(fmt)
    logging.basicConfig(
        level=logging.DEBUG,
        #format='{asctime} {process} {filename}:{lineno} {name} {levelname:8s} {message}',
        handlers=[fhandler, shandler]
    )

setup_logging()

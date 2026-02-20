from app.config import Settings, get_settings
from app.db import models, schemas, engine, SessionLocal, crud
import logging
import logging.handlers
from app.nflib.utils import *
import sys
import uuid 


def get_logger(n):
    alogger = logging.getLogger(n)
    alogger.setLevel(logging.DEBUG)
    fhandler = logging.handlers.RotatingFileHandler(
        f'logs/{n}.log', mode='a', encoding='utf-8', maxBytes=6000000, backupCount=10)
    fmt = logging.Formatter(
        '{asctime} {process} {filename}:{lineno} {name} {levelname:8s} {message}', style='{')
    fhandler.setFormatter(fmt)
    alogger.addHandler(fhandler)
    shandler = logging.StreamHandler()
    shandler.setFormatter(fmt)
    alogger.addHandler(shandler)
    return alogger


logger = get_logger("gen_redeem")


def gen_redeem(tag: str, count: str):
    try: 
        n = int(count)
    except Exception as err:
        logger.info("count must be an int, exit. %s", err)
        return 
    with SessionLocal() as db:
        for _ in range(n):
            redeem = models.Redeem(
                redeem_code = str(uuid.uuid4()),
                status = schemas.RedeemStatus.NEW.value,
                owner=tag
            )
            db.add(redeem)
            db.commit()


if __name__ == '__main__':
    gen_redeem(sys.argv[1], sys.argv[2])

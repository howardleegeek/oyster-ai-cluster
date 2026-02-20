import sys
from app.db import models, schemas, engine, SessionLocal, crud
import logging 
import logging.handlers


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


logger = get_logger("early_refer")


def add_early_referral(referrals):
    with open(referrals, "r") as f:
        with SessionLocal() as db:
            for line in f.readlines():
                logger.info("handling %s", line)
                addr, count = line.split(",")
                wallet_db = crud.get_wallet_by_address_b64(db=db, address_b64=addr)
                if wallet_db is None:
                    logger.info("wallet not found")
                    continue
                for _ in range(int(count)):
                    record = wallet_db.add_early_referrer()
                    db.add(record)
                db.commit()


if __name__ == '__main__':
    add_early_referral(sys.argv[1])

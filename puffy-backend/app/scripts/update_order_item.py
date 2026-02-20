from app.config import Settings, get_settings
from app.db import models, schemas, engine, SessionLocal, crud
from sqlalchemy.orm import Session
from typing import Union, Optional, List
import logging
import logging.handlers
from sqlalchemy import select, insert, update, delete, or_, and_
from app.nflib.utils import *
from sqlalchemy.orm import joinedload
import csv


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


logger = get_logger("export_order")


def get_orders(db: Session) -> List[models.Order]:
    return db.scalars(
        select(models.Order)
        .options(joinedload(models.Order.shipping_address, innerjoin=True))
        .options(joinedload(models.Order.ton_payment, innerjoin=True))
        .filter_by(status=schemas.OrderStatus.CONFIRMED.value)
    ).unique().all()


def export_order():
    # export all orders, including order_id, payment_wallet, date, amount, country
    with SessionLocal() as db:
        orders = get_orders(db=db)
        with open("data.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["order_id", "created_at", "owner", "country"])
            for o in orders:
                writer.writerow(
                    [o.id, o.created_at, o.ton_payment.from_address, o.shipping_address.country])


if __name__ == '__main__':
    export_order()

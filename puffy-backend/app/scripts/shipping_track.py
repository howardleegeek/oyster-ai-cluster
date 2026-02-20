import sys 
from app.config import Settings, get_settings
from app.db import models, schemas, engine, SessionLocal, crud
import logging
from typing import Union, Optional, List
import logging.handlers
from app.nflib.utils import *
import sys
import uuid 
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, insert, update, delete, or_, desc, asc
from sqlalchemy.orm import joinedload

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


logger = get_logger("st")


def get_orders(db: Session) -> List[models.Order]:
    return db.scalars(
        select(models.Order)
        .options(joinedload(models.Order.shipping_track, innerjoin=False))
        .filter_by(status=schemas.OrderStatus.CONFIRMED.value)
    ).unique().all()

def init_shipping_tracks():
    # get all confirmed orders and create st
    with SessionLocal() as db:
        orders = get_orders(db=db)
        for o in orders:
            if o.shipping_track is not None and len(o.shipping_track) > 0:
                logger.info("%s already has shipping track", o)
                continue
            for i in range(o.qty):
                st = models.ShippingTrack(
                    id=gen_random_id(),
                    order_id=o.id,
                    seq=i,
                    status=schemas.ShippingStatus.NEW.value
                )
                db.add(st)
                logger.info("create shipping track: %s", st)
                db.commit()


# def import_shipping_tracks(st_records: str):
#     with SessionLocal() as db:
#         with open(st_records, "r") as f:
#             for line in f:
#                 addr = line.strip()
#                 token = get_offchain_token_by_owner(db=db, token_type=token_type, owner=addr)
#                 if token is None:
#                     print("failed to find token for:", addr)
#                     continue
#                 print("update token on_chain True", addr) 
#                 token.on_chain = True 
#                 db.commit()

# def export_shipping_tracks(token_type: schemas.ItemType):
#     with SessionLocal() as db:
#         tokens = get_offchain_tokens(db=db, token_type=token_type)
#         with open(token_type.value + "_tokens.txt", "w") as f:
#             for t in tokens:
#                 if t.owner:
#                     f.write(t.owner + "\n")


if __name__ == '__main__':
    if sys.argv[1] == "init":
        init_shipping_tracks()
    # elif sys.argv[1] == "export":
    #     export_shipping_tracks(sys.argv[2])
    # elif sys.argv[1] == "import":
    #     import_shipping_tracks(sys.argv[2])

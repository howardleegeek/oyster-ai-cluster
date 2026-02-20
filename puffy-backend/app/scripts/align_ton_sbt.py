import sys 
from app.config import Settings, get_settings
from app.db import models, schemas, engine, SessionLocal, crud
import logging
import logging.handlers
from app.nflib.utils import *
import sys
import uuid 
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, insert, update, delete, or_, desc, asc

def get_offchain_token_by_owner(db: Session, token_type: schemas.ItemType, owner: str):
    if token_type == schemas.ItemType.FOUNDER:
        return db.scalars(
            select(models.FounderToken)
            .filter(models.FounderToken.owner==owner,
                    models.FounderToken.claimed==True,
                    (models.FounderToken.on_chain==None) | (models.FounderToken.on_chain==False))
            .limit(1)
        ).first()
    else:
        return db.scalars(
            select(models.FriendToken)
            .filter(models.FriendToken.owner==owner,
                    (models.FriendToken.on_chain==None) | (models.FriendToken.on_chain==False))
            .limit(1)
        ).first()

def get_offchain_tokens(db: Session, token_type: schemas.ItemType):
    if token_type == schemas.ItemType.FOUNDER:
        return db.scalars(
            select(models.FounderToken)
            .filter(models.FounderToken.claimed==True,
                    (models.FounderToken.on_chain==None) | (models.FounderToken.on_chain==False))
        ).all()
    else:
        return db.scalars(
            select(models.FriendToken)
            .filter((models.FriendToken.on_chain==None) | (models.FriendToken.on_chain==False))
        ).all()

def import_sbt(token_type: schemas.ItemType, sbt_list: str):
    with SessionLocal() as db:
        with open(sbt_list, "r") as f:
            for line in f:
                addr = line.strip()
                token = get_offchain_token_by_owner(db=db, token_type=token_type, owner=addr)
                if token is None:
                    print("failed to find token for:", addr)
                    continue
                print("update token on_chain True", addr) 
                token.on_chain = True 
                db.commit()

def export_token(token_type: schemas.ItemType):
    with SessionLocal() as db:
        tokens = get_offchain_tokens(db=db, token_type=token_type)
        with open(token_type.value + "_tokens.txt", "w") as f:
            for t in tokens:
                if t.owner:
                    f.write(t.owner + "\n")


if __name__ == '__main__':
    if sys.argv[1] == "import_founder":
        import_sbt(schemas.ItemType.FOUNDER, sys.argv[2])
    elif sys.argv[1] == "import_friend":
        import_sbt(schemas.ItemType.FRIEND, sys.argv[2])
    elif sys.argv[1] == "export_founder":
        export_token(schemas.ItemType.FOUNDER)
    elif sys.argv[1] == "export_friend":
        export_token(schemas.ItemType.FRIEND)

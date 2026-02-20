import logging 
from typing import List, Optional
from datetime import datetime
import uuid

from typing_extensions import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends 
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.models as models
import app.schemas as schemas 
from app.db.base import get_db
from app.db.err import *


logger = logging.getLogger(__name__)


class User:

    def __init__(self, db: Session):
        self.db = db

    def get_users(self, **kwargs) -> List[models.User]:
        logger.info("get users by condition %s", kwargs)
        return self.db.scalars(
            select(models.User)
                .options(joinedload(models.User.balance, innerjoin=True))
                .options(joinedload(models.User.referral_code))
                .options(joinedload(models.User.pass_code))
                .options(joinedload(models.User.records))
                .options(joinedload(models.User.nfts))
                .filter_by(**kwargs)
        ).unique().all()

    def get_user(self, **kwargs) -> Optional[models.User]:
        result = self.get_users(**kwargs)
        if result:
            return result[0]
        return None

    def create_or_get_user(self, address: str) -> models.User:
        user = self.get_user(address=address)
        if user:
            return user
        try:
            address_hex = None
            logger.info("create user with address %s", address)
            user = models.User(
                id=str(uuid.uuid4()),
                address=address,
                address_hex=address_hex,
                created_at=datetime.now())
            balance = models.Balance(
                points=0,
                referrals=0,
                indirect_referrals=0,
                usd=0,
                total_usd=0,
            )
            user.balance = balance
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as err:
            self.db.rollback()
            logger.warning("create user race condition for %s: %s", address, err)
            user = self.get_user(address=address)
            if user is None:
                raise err
            return user
    
    def update_user(self, user_id: str, **kwargs):
        user = self.get_user(id=user_id)
        if user is None:
            raise RecordNotFoundError(f"user {user_id} not found")
        for k, v in kwargs.items():
            if k in ["email", "twitter", "ton_address", "ton_address_hex"]:
                setattr(user, k, v)
            else:
                raise FieldNotFoundError(f"field {k} in user not found")
        self.commit()
    
    def commit(self):
        self.db.commit()
    
    
def get_user_repo(db: Session = Depends(get_db)):
    return User(db)


UserRepoDep = Annotated[User, Depends(get_user_repo)]

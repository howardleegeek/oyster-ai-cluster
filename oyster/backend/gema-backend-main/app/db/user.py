import logging 
from typing import List, Optional

from typing_extensions import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends 
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import app.models as models
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
                .options(joinedload(models.User.records))
                .options(joinedload(models.User.nfts))
                .options(joinedload(models.User.orders))
                .filter_by(**kwargs)
        ).unique().all()

    def get_user(self, **kwargs) -> Optional[models.User]:
        result = self.get_users(**kwargs)
        if result:
            return result[0]
        return None

    def create_or_get_user(self, address: str) -> models.User:
        try:
            user = self.get_user(sol_address=address)
            if user:
                return user
            logger.info("create user with address %s", address)
            user_db = models.User(
                id=str(uuid.uuid4()),
                sol_address=address,
                created_at=datetime.now())
            balance_db = models.Balance(
                points=0,
                referrals=0,
            )
            user_db.balance = balance_db
            self.db.add(user_db)
            self.db.commit()
            self.db.refresh(user_db)
            return user_db
        except IntegrityError as err:
            self.db.rollback()
            logger.error("create user failed %s %s", address, err)
            return self.get_user(sol_address=address)
    
    def update_user(self, user_id: str, **kwargs):
        user_db = self.get_user(id=user_id)
        if user_db is None:
            raise RecordNotFoundError(f"user {user_id} not found")
        for k, v in kwargs.items():
            if k in ["email", "twitter_id", "twitter_name"]:
                setattr(user_db, k, v)
            else:
                raise FieldNotFoundError(f"field {k} in user not found")
        self.db.commit()
    

def get_user_repo(db: Session = Depends(get_db)):
    return User(db)


UserRepoDep = Annotated[User, Depends(get_user_repo)]


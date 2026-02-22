import logging 
from typing import Optional

from typing_extensions import Annotated
from fastapi import Depends

from app.db.user import User as UserRepo, UserRepoDep
import app.schemas as schemas


logger = logging.getLogger(__name__)


class User:

    def __init__(self, repo: UserRepo):
        self.repo = repo

    def create_or_get_user(self, address: str) -> Optional[schemas.User]:
        user_db = self.repo.create_or_get_user(address)
        if user_db is None:
            return None
        return schemas.User.model_validate(user_db)
    
    def get_user(self, **kwargs) -> Optional[schemas.User]:
        user_db = self.repo.get_user(**kwargs)
        if user_db is None:
            return None
        return schemas.User.model_validate(user_db)

    def update_user(self, user_id: str, **kwargs):
        self.repo.update_user(user_id=user_id, **kwargs)


def get_user_service(
    repo: UserRepoDep):
    return User(repo)


UserServiceDep = Annotated[User, Depends(get_user_service)]


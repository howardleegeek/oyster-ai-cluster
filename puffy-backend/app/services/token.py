from typing_extensions import Annotated
import logging 
import time
from typing import List, Optional

import jwt
from fastapi import Depends

from app.config import SettingsDep
from app.schemas.user import User 


logger = logging.getLogger(__name__)


class Token:

    def __init__(self, secret: str, exp: int):
        self.secret = secret
        self.exp = exp

    def gen_token(self, user: User) -> str:
        payload = {
            "id": user.id,
            "address": user.address,
            "exp": int(time.time() + self.exp),
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def parse_token(self, token: Optional[str]) -> Optional[User]:
        if token is None:
            logger.info("token is None, skip parsing")
            return None
        try:
            # in case token is "Bearer token"
            if " " in token:
                token = token.split(" ")[1]
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return User(
                id=payload.get("id"),
                address=payload.get("address")
            )
        except jwt.ExpiredSignatureError:
            logger.info("expired token %s...", token[:20] if token else "empty")
            return None
        except jwt.InvalidTokenError:
            logger.info("invalid token %s...", token[:20] if token else "empty")
            return None
        except Exception as err:
            logger.error("parse token error %s... %s", token[:20] if token else "empty", err)
            return None

def get_token_service(settings: SettingsDep) -> Token:
    return Token(settings.secret, settings.id_exp)


TokenServiceDep = Annotated[Token, Depends(get_token_service)]



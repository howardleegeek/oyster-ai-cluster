from pydantic import BaseModel, TypeAdapter
import hashlib 
import hmac
import datetime 
import logging 
from typing import Optional

from fastapi import Depends

from app.config import SettingsDep


logger = logging.getLogger(__name__)


def get_tg_service(settings: SettingsDep):
    return TgService(settings.tg_token, settings.tg_chat_id)


class TgOauth(BaseModel):
    id: str
    hash: str 
    auth_date: int 
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    photo_url: Optional[str]


class TgService:

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def check_auth(self, auth_data: TgOauth) -> bool:
        data_checks = []
        for key, value in auth_data.dict().items():
            if key != "hash":
                data_checks.append(f"{key}={value}")

        secret_key = hashlib.sha256(self.token.encode('utf-8')).digest()
        gen_hash = hmac.new(
            secret_key, 
            "\n".join(data_checks).encode('utf-8'), 
            hashlib.sha256).hexdigest()

        if gen_hash != auth_data.hash:
            logger.info("hash not match %s %s %s", 
                        auth_data.first_name, gen_hash, auth_data.hash)
            return False

        if (datetime.datetime.now(datetime.timezone.utc).timestamp 
            - 
            auth_data.auth_date) > 86400:
            logger.info("auth expired %s", auth_data.first_name)
            return False

        return True

    def get_users(self):
        pass 
    
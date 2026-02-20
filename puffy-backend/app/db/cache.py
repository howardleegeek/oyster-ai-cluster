from pydantic import BaseModel
import logging
import redis
import uuid
from typing import Optional
from datetime import timedelta
from typing_extensions import Annotated
from fastapi import Depends
import app.schemas as schemas
from app.config import Settings, get_settings, SettingsDep


logger = logging.getLogger(__name__)


class CacheDb:
    #def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
    def __init__(self, settings: Settings):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db)
        self.session_ttl = settings.session_ttl

    def new_session(self, data: schemas.SessionData):
        session_id = str(uuid.uuid4())
        data_json = data.model_dump_json()
        self.redis_client.setex(session_id, value=data_json, time=self.session_ttl)
        return session_id

    def get_session(self, session_id: str) -> Optional[schemas.SessionData]:
        data = self.redis_client.get(session_id)
        if data is None:
            logger.info("session not found or expired %s", session_id)
            return None
        try:
            return schemas.SessionData.model_validate_json(data)
        except Exception as err:
            logger.error("parse session data failed %s", err)
            return None

    def set_data(self, key: str, data: str, exp: int = 12):
        self.redis_client.set(key, data, ex=timedelta(hours=exp))

    def get_data(self, key: str) -> Optional[str]:
        result = self.redis_client.get(key)
        if result:
            return result.decode(encoding="utf-8")
        return None

    def close_session(self, session_id):
        self.redis_client.delete(session_id)


_CACHE_INSTANCE = CacheDb(get_settings())


def get_cache_db():
    try:
        return _CACHE_INSTANCE
    except Exception as err:
        logger.error("get cache db failed %s", err)
        

CacheDbDep = Annotated[CacheDb, Depends(get_cache_db)]


if __name__ == '__main__':
    from app.config import get_settings
    storage = CacheDb(get_settings())
    a = storage.new_session(schemas.SessionData(message="test", wallet_address="0x1234"))
    print(a)
    otp = storage.get_session(a)
    print(otp)

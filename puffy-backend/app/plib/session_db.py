# DEPRECATED: This module is superseded by app.db.cache.CacheDb, which provides
# a unified Redis-backed session and cache store with configurable settings.
# Retained for backward compatibility only. Do not use in new code.

from .utils import *
from pydantic import BaseModel
import logging
import redis
import uuid
from typing import Optional
from datetime import timedelta

logger = logging.getLogger("up")


class SessionDbData(BaseModel):
    message: str
    email: Optional[str] = None


class SessionDb:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db)

    def new_session(self, data: SessionDbData):
        session_id = str(uuid.uuid4())
        data_json = data.model_dump_json()
        self.redis_client.setex(session_id, value=data_json, time=600)
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionDbData]:
        data = self.redis_client.get(session_id)
        if data is None:
            logger.info("session not found or expired %s", session_id)
            return None
        try:
            return SessionDbData.model_validate_json(data)
        except Exception as err:
            logger.error("parse session data failed %s", err)
            return None

    def cache_data(self, key: str, data: str, exp: int = 12):
        self.redis_client.set(key, data, ex=timedelta(hours=exp))

    def get_data(self, key: str) -> Optional[str]:
        return self.redis_client.get(key)

    def close_session(self, session_id):
        self.redis_client.delete(session_id)


if __name__ == '__main__':
    storage = SessionDb()
    a = storage.new_session("1234567890")  # Store OTP for 60 seconds
    print(a)
    # Get stored OTP (valid for 60 seconds)
    otp = storage.get_session(a)
    print(otp)

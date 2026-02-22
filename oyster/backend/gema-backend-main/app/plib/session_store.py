import time
import threading
import logging
from pydantic import BaseModel

logger = logging.getLogger("up")


class SessionData(BaseModel):
    message: str
    wallet_address: str
    exp_time: int = int(time.time() + 600)

    def expire(self):
        return time.time() > self.exp_time


class SessionStore:
    def __init__(self):
        self._sessions = {}
        self._lock = threading.Lock()

    def new_session(self, data: SessionData):
        with self._lock:
            self._sessions[data.wallet_address] = data
            return data.wallet_address

    def get_session(self, session_id) -> SessionData:
        with self._lock:
            session_info = self._sessions.get(session_id)
            if session_info is None:
                logger.info("session not found %s", session_id)
                return None
            if session_info.expire():
                logger.info("session expired %s", session_id)
                # Remove expired session
                self._sessions.pop(session_id)
                return None
            return session_info

    def close_session(self, session_id):
        with self._lock:
            self._sessions.pop(session_id)


if __name__ == '__main__':
    storage = SessionStore()
    a = storage.new_session("1234567890")  # Store OTP for 60 seconds
    print(a)
    # Get stored OTP (valid for 60 seconds)
    otp = storage.get_session(a)
    print(otp)

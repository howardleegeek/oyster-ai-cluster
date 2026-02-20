from enum import Enum, auto
from fastapi import HTTPException


class UserError(Enum):
    INVALID_SESSION = auto()
    INVALID_SIGNATURE = auto()
    INVALID_OTP_CODE = auto()
    USER_NOT_FOUND = auto()
    USER_NOT_ELIGIBLE = auto()
    USER_ELIGIBLE = auto()
    WALLET_NOT_FOUND = auto()
    WALLET_TOKEN_MISSING = auto()
    WALLET_BALANCE_NOT_ENOUGH = auto()
    USER_NOT_FOUNDER = auto()
    USER_FOUNDER_CLAIMED = auto()
    NOT_ENOUGH_BALANCE = auto()
    USER_IS_FOUNDER = auto()
    USER_IS_FRIEND = auto()
    INVALID_REF_CODE = auto()
    INVALID_RED_CODE = auto()
    INVALID_REQUEST = auto()
    DOUBLE_REF = auto()
    OAUTH_FAILED = auto()

    def http(self, status_code: int = 404):
        return HTTPException(status_code=status_code, detail=self.name)


class ServerError(Enum):
    DB_ERROR = auto()
    SERVER_BUSY = auto()

    def http(self):
        return HTTPException(status_code=500, detail=self.name)

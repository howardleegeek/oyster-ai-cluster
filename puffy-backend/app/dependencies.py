from typing_extensions import Annotated
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services import TokenServiceDep
import app.schemas as schemas


security = HTTPBearer()


def get_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: TokenServiceDep
) -> schemas.User:
    """Dependency to get current authenticated user from JWT token"""
    user_info = token_service.parse_token(token.credentials)
    if user_info is None:
        raise HTTPException(
            status_code=401, detail="Missing authentication credentials")
    return user_info


UserAuthDep = Annotated[schemas.User, Depends(get_user)]

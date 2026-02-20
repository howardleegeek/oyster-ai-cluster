from typing import List, Optional
import logging

from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.error import UserError, ServerError
from app.utils import SuccessResp, SettingsDep, SolDep
from app.plib import *

from app.ext_service import *
from app.services import * 
import app.schemas as schemas
from app.db import *
from app.dependencies import UserAuthDep
from app.db import CacheDbDep


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


logger = logging.getLogger(__name__)


@router.get("/sign-in")
def sign_in_user(cache_db: CacheDbDep) -> schemas.SessionInfo:
    # Generate a random message
    message = gen_random_hex_str(20)
    # Store the message and user address for later verification
    session_data = schemas.SessionData(message=message)
    session_id = cache_db.new_session(session_data)
    logger.info("sign in user returns msg: %s, session: %s",
                message, session_id)
    return schemas.SessionInfo(session_id=session_id, message=message)


class UserVerify(BaseModel):
    session_id: str
    address: str
    signature: str


security = HTTPBearer()


def get_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: TokenServiceDep
) -> schemas.User:
    user_data = token_service.parse_token(token.credentials)
    if user_data is None:
        raise HTTPException(
            status_code=401, detail="Missing authentication credentials")
    return user_data


UserAuthDep = Annotated[schemas.User, Depends(get_user)]


class TwitterOauth(BaseModel):
    auth_code: str
    redirect_url: str


class TokenResp(BaseModel):
    token: str


@router.post("/verify")
def verify_user(
    req: UserVerify,
    cache_db: CacheDbDep,
    sol: SolDep,
    user_service: UserServiceDep,
    token_service: TokenServiceDep
) -> TokenResp:
    session_data = cache_db.get_session(req.session_id)
    if not session_data:
        logger.info("session id not found %s", req.session_id)
        raise UserError.INVALID_SESSION.http()

    message = session_data.message
    if not message:
        logger.info("session data not found %s", req.session_id)
        raise UserError.INVALID_SESSION.http()

    result = sol.verify(
        bytes(message, "utf-8"),
        req.signature,
        req.address
        )
    if not result:
        logger.info("invalid signature %s", req.address)
        raise UserError.INVALID_SIGNATURE.http()

    user = user_service.create_or_get_user(req.address)
    token = token_service.gen_token(user)
    # Invalidate session to prevent signature replay attacks
    cache_db.close_session(req.session_id)
    logger.debug("token generated %s", token)
    return TokenResp(token=token)


@router.get("/me")
def get_current_user(
    user: UserAuthDep,
    user_service: UserServiceDep
) -> schemas.User:
    user_info = user_service.get_user(id=user.id)
    if user_info is None:
        logger.info("user id not found %s", user.id)
        raise UserError.INVALID_REQUEST.http()
    return user_info


class TwitterOauth(BaseModel):
    auth_code: str
    state: Optional[str] = None  # OAuth state param that maps to a cached PKCE verifier


@router.post("/twitter-oauth")
def update_user_twitter(
    req: TwitterOauth,
    user: UserAuthDep,
    user_service: UserServiceDep,
    settings: SettingsDep,
    cache_db: CacheDbDep,
) -> SuccessResp:
    # Look up the PKCE code_verifier from cache if state is provided.
    # Falls back to 'challenge' for backward compatibility with frontends
    # that haven't implemented PKCE yet.
    code_verifier = "challenge"
    if req.state:
        cached_verifier = cache_db.get_data(f"pkce:{req.state}")
        if cached_verifier:
            code_verifier = cached_verifier

    twitter_id = twitter_oauth(
        settings.twitter_id,
        settings.twitter_secret,
        req.auth_code,
        settings.twitter_redirect_url,
        code_verifier=code_verifier,
    )
    if twitter_id is None:
        logger.info("oauth failed")
        raise UserError.INVALID_REQUEST.http()
    try:
        logger.info("oauth return twitter id %s", twitter_id)
        user_service.update_user(
            user_id=user.id,
            twitter=twitter_id)
        return SuccessResp()
    except Exception as err:
        logger.error("update twitter for user %s failed: %s", user.id, err)
        raise ServerError.DB_ERROR.http()


class UpdateEmailReq(BaseModel):
    email: str


@router.post("/update-email")
def update_user_email(
    req: UpdateEmailReq,
    user: UserAuthDep,
    user_service: UserServiceDep
) -> SuccessResp:
    try:
        user_service.update_user(
            user_id=user.id,
            email=req.email)
        return SuccessResp()
    except Exception as err:
        logger.error("update email for user %s failed: %s", user.id, err)
        raise ServerError.DB_ERROR.http()


@router.get("/eligible-products")
def get_eligible_products(
    user: UserAuthDep,
    user_service: UserServiceDep,
    product_service: ProductServiceDep
) -> List[schemas.Product]:
    products = product_service.get_products()
    return user_service.get_eligible_products(user_id=user.id, products=products)

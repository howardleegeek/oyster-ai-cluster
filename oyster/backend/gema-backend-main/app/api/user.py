from typing import List
import logging

from typing_extensions import Annotated
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel

from app.error import UserError, ServerError
from app.utils import SolDep
from app.plib import *
from app.ext_service import *
from app.services import *
import app.schemas as schemas
from app.db import *
from app.enums import OrderStatus

import traceback


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


logger = logging.getLogger(__name__)


security = HTTPBearer()


def get_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: TokenServiceDep
) -> schemas.User:
    user_info = token_service.parse_token(token.credentials)
    if user_info is None:
        raise HTTPException(
            status_code=401, detail="Missing authentication credentials")
    return user_info


UserAuthDep = Annotated[schemas.User, Depends(get_user)]


@router.get("/sign-in")
def sign_in_user(cache_db: CacheDbDep) -> schemas.SessionInfo:
    # Generate a random message
    message = gen_random_hex_str(20)
    # Store the message and wallet address for later verification
    session_data = schemas.SessionData(message=message)
    session_id = cache_db.new_session(session_data)
    logger.info("sign in wallet returns msg: %s, session: %s",
                message, session_id)
    return schemas.SessionInfo(session_id=session_id, message=message)


class WalletVerify(BaseModel):
    session_id: str
    address: str
    signature: str


class TokenResp(BaseModel):
    token: str


class SuccessResp(BaseModel):
    status: str = "success"


@router.post("/verify")
def verify_user(
    req: WalletVerify,
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
    logger.debug("token generated %s", token)
    return TokenResp(token=token)


@router.get("/info")
def get_user_info(
    user: UserAuthDep,
    user_service: UserServiceDep
) -> schemas.User:
    user_info = user_service.get_user(id=user.id)
    if user_info is None:
        logger.info("user id %s not found", user.id)
        raise UserError.INVALID_REQUEST.http()
    return user_info


@router.get("/orders")
def get_orders(
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> List[schemas.Order]:
    return order_service.get_orders(user_id=user.id)


@router.post("/orders")
def create_order(
    req: schemas.Order,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> schemas.Order:
    logger.info("create order %s", req)
    req.user_id = user.id
    try: 
        return order_service.create_order(req)
    except Exception as err:
        traceback.print_exc()
        logger.error("create order failed %s", err)
        raise UserError.INVALID_REQUEST.http()


@router.put("/orders/{order_id}")
def update_order_shipping_address(
    order_id: str,
    req: schemas.ShippingAddress,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> SuccessResp:
    try:
        order_service.update_order_shipping_address(
            user_id=user.id,
            order_id=order_id,
            address=req
        )
        return SuccessResp()
    except Exception as err:
        logger.error("update address failed %s", err)
        raise UserError.INVALID_REQUEST.http()


class PayReq(BaseModel):
    transaction_id: str


@router.post("/orders/{order_id}")
def pay_order(
    order_id: str,
    req: PayReq,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> SuccessResp:
    # for sol payment with usdc, pay order creates a payment record with transaction_id
    # later will be updated by background job
    try:
        order = order_service.get_order(id=order_id)
        if order is None or order.status != OrderStatus.NEW:
            logger.info("order %s not found or status wrong", order_id)
            raise UserError.INVALID_REQUEST.http()
        logger.info("update order %d status to PAID", order_id)
        order_service.update_order_status(order_id, OrderStatus.PAID)
        ogger.info("create payment for order %d", order_id)
        order_service.create_payment(
            user_id=user.id,
            order_id=order_id,
            transaction_id=req.transaction_id
        )
        return SuccessResp()
    except Exception as err:
        logger.error("create payment failed %s", err)
        raise UserError.INVALID_REQUEST.http()


class TwitterOauth(BaseModel):
    auth_code: str


@router.post("/twitter-oauth")
def twitter_oauth(
    req: TwitterOauth,
    user: UserAuthDep,
    user_service: UserServiceDep
) -> SuccessResp:
    """
    Docstring for twitter_oauth
    
    :param req: Description
    :type req: TwitterOauth
    :param user: Description
    :type user: UserAuthDep
    :param user_service: Description
    :type user_service: UserServiceDep
    :return: Description
    :rtype: SuccessResp
    """
    twitter_result = oauth.twitter_oauth(
        settings.twitter_id,
        settings.twitter_secret,
        req.auth_code,
        settings.twitter_redirect_url
    )
    if twitter_id is None:
        logger.info("oauth failed")
        raise UserError.INVALID_REQUEST.http()
    try:
        logger.info("oauth return twitter result %s", twitter_result)
        user_service.update_user(
            user_id=user.id,
            twitter_id=twitter_result["id"],
            twitter_name=twitter_result["name"])
        return SuccessResp()
    except Exception:
        logger.error("update twitter for user %s failed", user.id)
        raise ServerError.DB_ERROR.http()


class EmailReq(BaseModel):
    email: str 
    

@router.post("/email")
def update_user_email(
    req: EmailReq,
    user: UserAuthDep,
    user_service: UserServiceDep
) -> SuccessResp:
    try:
        user_service.update_user(
            user_id = user.id,
            email = req.email
        )
        return SuccessResp()
    except Exception:
        logger.error("update user %s email %s failed", user.id, req.email)
        raise UserError.INVALID_REQUEST.http()


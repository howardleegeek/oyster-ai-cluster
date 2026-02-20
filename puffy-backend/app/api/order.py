from typing import List, Optional
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.error import UserError, ServerError
from app.utils import SuccessResp
from app.services import OrderServiceDep
import app.schemas as schemas
from app.db import *
from app.enums import OrderStatus
from app.dependencies import UserAuthDep


router = APIRouter(
    prefix="/order",
    tags=["Order"]
)


logger = logging.getLogger(__name__)


@router.get("/")
def get_orders(
    user: UserAuthDep,
    order_service: OrderServiceDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[schemas.Order]:
    return order_service.get_orders(user_id=user.id, limit=limit, offset=offset)


@router.get("/{order_id}")
def get_order(
    order_id: str,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> schemas.Order:
    order = order_service.get_order(user_id=user.id, id=order_id) 
    if order:
        return order
    logger.info("no order %s found for user %s", order_id, user.id)
    raise UserError.INVALID_REQUEST.http()


@router.post("/")
def create_order(
    req: schemas.OrderCreate,
    user: UserAuthDep,
    order_service: OrderServiceDep,
    dry_run: bool = Query(False, description="Calculate only, don't create order")
) -> schemas.Order:
    """Create a new order with shipping address and items."""
    logger.info("create order %s for user %s", req, user.id)
    try:
        if dry_run:
            return order_service.dry_run_create_order(user, req)
        return order_service.create_order(user, req)
    except Exception as err:
        logger.error("create order failed %s", err)
        raise UserError.INVALID_REQUEST.http()


@router.put("/{order_id}/shipping-address")
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


@router.post("/{order_id}/pay")
def pay_order(
    order_id: str,
    req: PayReq,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> SuccessResp:
    # for sol payment with usdc, pay order creates a payment record with transaction_id
    # later will be updated by background job
    try:
        order_service.create_payment(
            user_id=user.id,
            order_id=order_id,
            transaction_id=req.transaction_id
        )
        return SuccessResp()
    except Exception as err:
        logger.error("create payment failed %s", err)
        raise UserError.INVALID_REQUEST.http()


class ValidatePasscodeReq(BaseModel):
    passcode: str


class ValidatePasscodeResp(BaseModel):
    valid: bool


@router.post("/validate-passcode")
def validate_passcode(
    req: ValidatePasscodeReq,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> ValidatePasscodeResp:
    """Validate a passcode"""
    try:
        valid = order_service.validate_passcode(req.passcode)
        return ValidatePasscodeResp(valid=valid)
    except NotImplementedError as err:
        logger.error("validate passcode failed: %s", err)
        raise HTTPException(status_code=501, detail=str(err))
    except Exception as err:
        logger.error("validate passcode failed: %s", err)
        raise UserError.INVALID_REQUEST.http()


class ValidateReferralCodeReq(BaseModel):
    referral_code: str


class ValidateReferralCodeResp(BaseModel):
    valid: bool
    owner_id: Optional[str] = None
    max_uses: Optional[int] = None
    current_uses: Optional[int] = None


@router.post("/validate-referralcode")
def validate_referralcode(
    req: ValidateReferralCodeReq,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> ValidateReferralCodeResp:
    """Validate a referral code and return its details if valid"""
    try:
        valid, owner_id, max_uses, current_uses = order_service.validate_referralcode(
            referral_code=req.referral_code
        )
        return ValidateReferralCodeResp(
            valid=valid,
            owner_id=owner_id,
            max_uses=max_uses,
            current_uses=current_uses
        )
    except NotImplementedError as err:
        logger.error("validate referral code failed: %s", err)
        raise HTTPException(status_code=501, detail=str(err))
    except Exception as err:
        logger.error("validate referral code failed: %s", err)
        raise UserError.INVALID_REQUEST.http()


@router.delete("/{order_id}")
def cancel_order(
    order_id: str,
    user: UserAuthDep,
    order_service: OrderServiceDep
) -> SuccessResp:
    """Cancel order by setting status to CANCELLED"""
    try:
        order_service.cancel_order(
            order_id=order_id,
            user_id=user.id
        )
        return SuccessResp()
    except NotImplementedError as err:
        logger.error("cancel order failed: %s", err)
        raise HTTPException(status_code=501, detail=str(err))
    except Exception as err:
        logger.error("cancel order failed: %s", err)
        raise UserError.INVALID_REQUEST.http()

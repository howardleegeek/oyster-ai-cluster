import logging


logger = logging.getLogger("up")


def get_payment_on_chain(user, transaction_hash):
    try:
        logger.info("get payment on chain for %s", transaction_hash)
        # call blockchain api to get payment status
        # return payment status
        return True
    except Exception as err:
        logger.error("get payment on chain failed %s", err)
        return None


def get_proxy_price(url) -> float:
    try:
        # call proxy api to get price
        # return price
        return 5.4
    except Exception as err:
        logger.error("get proxy price failed %s", err)
        return 0

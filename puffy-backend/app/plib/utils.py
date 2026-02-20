from functools import lru_cache, wraps
from time import monotonic_ns
import random
import hashlib
import string
from pytoniq_core import Address


def addr_hex_to_b64(addr: str, test_net: bool = False):
    try:
        a = Address(addr)
        return a.to_str(is_bounceable=False, is_test_only=test_net)
    except Exception as err:
        logger.error("format addr failed %s", err)
        return addr
    

def addr_b64_to_hex(b64: str) -> str:
    try:
        a = Address(b64)
        return a.to_str(is_user_friendly=False)
    except Exception as err:
        logger.error("format addr failed %s", err)
        return b64


def gen_random_id(id_len: int=15):
    return ''.join(
        random.choices(
            string.digits + string.ascii_lowercase, k=id_len))


# generate session id
def gen_random_hex_str(length=20):
    random_bytes = bytearray(random.randint(0, 255)
                             for _ in range(length))
    hex_string = "".join(f"{byte:02x}" for byte in random_bytes)
    return hex_string


def gen_random_otp():
    return str(random.randint(100000, 999999))


# generate user id
def sha256(phone_number):
    m = hashlib.sha256()
    m.update(bytes(phone_number, 'utf-8'))
    return m.hexdigest()


def timed_lru_cache(
    _func=None, *, seconds: int = 600, maxsize: int = 128, typed: bool = False
):
    """Extension of functools lru_cache with a timeout

    Parameters:
    seconds (int): Timeout in seconds to clear the WHOLE cache, default = 10 minutes
    maxsize (int): Maximum Size of the Cache
    typed (bool): Same value of different type will be a different entry
    """

    def wrapper_cache(f):
        f = lru_cache(maxsize=maxsize, typed=typed)(f)
        f.delta = seconds * 10 ** 9
        f.expiration = monotonic_ns() + f.delta

        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if monotonic_ns() >= f.expiration:
                f.cache_clear()
                f.expiration = monotonic_ns() + f.delta
            return f(*args, **kwargs)

        wrapped_f.cache_info = f.cache_info
        wrapped_f.cache_clear = f.cache_clear
        return wrapped_f

    # To allow decorator to be used without arguments
    if _func is None:
        return wrapper_cache
    else:
        return wrapper_cache(_func)


if __name__ == '__main__':
    print(gen_random_hex_str(20))
    print(gen_random_hex_str(20))
    print(gen_random_hex_str(20))

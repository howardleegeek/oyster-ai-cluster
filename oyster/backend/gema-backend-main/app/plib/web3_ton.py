import logging
from nacl.utils import random
from datetime import datetime
from pydantic import BaseModel
from pytonconnect.parsers import WalletInfo, Account, TonProof
from pytoniq_core import crypto
import json

logger = logging.getLogger("up")


class Proof(BaseModel):
    signature: str
    state_init: str
    timestamp: int
    public_key: str
    wallet_address_hex: str
    wallet_address_base64: str

class TonWrapper:
    def verify_proof(proof: Proof,
                    payload: str,
                    domain: str,
                    network: int) -> bool:
        logger.info('verify proof %s', proof)
        logger.info('payload %s', payload)
        logger.info('domain %s', domain)
        logger.info('network %s', network)
        account = Account.from_dict({
            'address': proof.wallet_address_hex, 'network': network,
            'walletStateInit': proof.state_init, 'publicKey': proof.public_key})
        tp = TonProof.from_dict({
            'proof': {
                'timestamp': proof.timestamp,
                'payload': payload,
                'signature': proof.signature,
                'domain': {
                    'lengthBytes': len(domain),
                    'value': domain
                }
            }})
        wi = WalletInfo()
        wi.account = account
        wi.ton_proof = tp
        return wi.check_proof(payload)


def up_sign(payload: dict, key: str) -> str:
    bytes_to_sign = bytes(json.dumps(payload))
    signing_key = crypto.keys.mnemonic_to_private_key(key)
    return crypto.signature.sign_message(bytes_to_sign, signing_key=signing_key)


def gen_payload(ttl: int) -> str:
    payload = bytearray(random(8))

    ts = int(datetime.now().timestamp()) + ttl
    payload.extend(ts.to_bytes(8, 'big'))

    return payload.hex()


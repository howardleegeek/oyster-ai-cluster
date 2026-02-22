from base58 import b58decode, b58encode
from nacl.signing import VerifyKey, SigningKey
from nacl.exceptions import BadSignatureError
import logging
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class SolWrapper(BaseModel):

    key: str
        
    def verify(self, message: bytes, signature: str, public_key: str) -> bool:
        try:
            # Decode the base58 public key and signature
            decoded_public_key = b58decode(public_key)
            decoded_signature = b58decode(signature)
            
            # Create a VerifyKey instance from the public key
            verify_key = VerifyKey(bytes(decoded_public_key))
            
            # Verify the signature
            verify_key.verify(message, bytes(decoded_signature))
            return True
            
        except BadSignatureError as err:
            logger.info("invalid signature %s %s %s", public_key, signature, err)
            return False
        except Exception as err:
            logger.info("verify signature failed %s %s %s", public_key, signature, err)

    def sign(self, message: str) -> str:
        try:
            message_b = b58decode(message)
            decoded_key = b58decode(self.key)
            sol_key = SigningKey(bytes(decoded_key)[0:32])
            signed_msg = sol_key.sign(bytes(message_b))[0:64]
            return b58encode(signed_msg).decode("utf-8")
        except Exception as err:
            logger.info("sign message failed %s %s", message, err)
            return None


if __name__ == '__main__':
    verifier = SolWrapper("some_key")
    message = b"Hello, world!"
    signature = "signature"
    public_key = "public_key"
    
    result = verifier.verify(message, signature, public_key)
    print(result)

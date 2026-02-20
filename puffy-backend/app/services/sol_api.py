import logging 
from typing import Optional, List

from typing_extensions import Annotated
from fastapi import Depends
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
from spl.token.constants import TOKEN_PROGRAM_ID

from app.db.wallet import Wallet as WalletRepo, get_wallet_repo
import app.schemas as schemas
from app.config import SettingsDep, Settings
from app.plib.utils import addr_b64_to_hex


logger = logging.getLogger(__name__)


class SolApi:

    TOKEN_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

    def __init__(self, settings: Settings):
        self.url = settings.sol_api_url
        self.wallet_address = settings.sol_taker_address
        self.wallet_pub_key = PublicKey(self.wallet_address)
        self.client = Client(self.url)

    def get_nfts(self, address: str) -> Optional[schemas.CommunityNft]:
        wallet_address = PublicKey(address)
        token_accounts = self.client.get_token_accounts_by_owner(
            wallet_address,
            TokenAccountOpts(program_id=TOKEN_PROGRAM_ID),
            encoding="jsonParsed"
        )
        result = []
        for token_account in token_accounts:
            result.append(schemas.CommunityNft(
                nft_address=token_account["account"]["data"]["parsed"]["info"]["tokenAccount"]["address"],
                nft_collection=token_account["account"]["data"]["parsed"]["info"]["tokenAccount"]["tokenAmount"]["mint"],
                chain='sol',
                meta_name=token_account["account"]["data"]["parsed"]["info"]["tokenAccount"]["tokenAmount"]["mint"],
                meta_image=token_account["account"]["data"]["parsed"]["info"]["tokenAccount"]["tokenAmount"]["mint"],
                meta_content_url=token_account["account"]["data"]["parsed"]["info"]["tokenAccount"]["tokenAmount"]["mint"],
                meta_description=token_account["account"]["data"]["parsed"]["info"]["tokenAccount"]["tokenAmount"]["mint"]))
        return result
    
    def get_transactions(self) -> List[schemas.Payment]:
        signatures = self.client.get_signatures_for_address(self.wallet_address)["result"]
        result = []
        for signature in signatures:
            tx = self.client.get_transaction(signature)["result"]
            for instruction in tx["transaction"]["message"]["instructions"]:
                if ("parsed" in instruction and 
                    instruction["parsed"]["info"]["destination"] == str(self.wallet_address)):
                    result.append(tx)
        return result

def get_tonapi_service(settings: SettingsDep):
    return TonApi(settings)


TonApiDep = Annotated[TonApi, Depends(get_tonapi_service)]

       

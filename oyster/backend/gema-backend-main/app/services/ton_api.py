import logging 
from typing import Optional

from typing_extensions import Annotated
from fastapi import Depends

import app.schemas as schemas
from app.config import SettingsDep, Settings
from app.plib.utils import addr_b64_to_hex


logger = logging.getLogger(__name__)


class TonApi:

    def __init__(self, settings: Settings):
        self.url = settings.ton_api_url
        self.key = settings.ton_api_key

    def get_nfts(self, address: str) -> Optional[schemas.CommunityNft]:
        hex_addr = addr_b64_to_hex(address)
        url = f"https://{self.url}/v2/accounts/{hex_addr}/nfts"
        headers = {'Authorization': f"Bearer {self.key}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error("Failed to get transactions %s", response.text)
                return []
            items = response.json()['nft_items']
            result = []
            for item in items:
                result.append(schemas.CommunityNft(
                    nft_address=item['address'],
                    nft_collection=item['owner']['collection']['address'],
                    meta_name=item['owner']['metadata']['name'],
                    meta_image=item['owner']['metadata']['image'],
                    meta_content_url=item['owner']['metadata']['external_url'],
                    meta_description=item['owner']['metadata']['description'],
                    chain='ton'))
            return result
        except Exception as err:
            logger.error("calling tonapi failed %s", err)
            return []


def get_tonapi_service(settings: SettingsDep):
    return TonApi(settings)


TonApiDep = Annotated[TonApi, Depends(get_tonapi_service)]

       

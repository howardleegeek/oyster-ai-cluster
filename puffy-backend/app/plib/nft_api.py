import logging
import requests
from functools import lru_cache
from app.config import Settings, get_settings
from typing_extensions import Annotated
from fastapi import Depends
import app.schemas as schemas 
from typing import List 

from app.schemas.user import NftCollectionMeta


logger = logging.getLogger(__name__)


class NftApi:

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url 
        self.api_key = api_key 


    @lru_cache(maxsize=128)
    def get_collection_meta(self, nft_collection_meta_id: int) -> NftCollectionMeta:
        try:
            resp = requests.get(
                f"{self.api_url}/nft-collection-meta/{nft_collection_meta_id}", 
                headers={"api-key": self.api_key})
            if resp.status_code not in [200, 201]:
                return None 
            result = resp.json()
            return NftCollectionMeta.model_validate(result)
        except Exception as err:
            logger.error("get collection metadata failed %s", err)
            return None 


    def get_next_sequence(self, nft_collection_meta_id: int)  -> int:
        try:
            resp = requests.get(
                f"{self.api_url}/nft-collection-meta/{nft_collection_meta_id}/next-sequence", 
                headers={"api-key": self.api_key})
            if resp.status_code not in [200, 201]:
                return None 
            return int(resp.content)
        except Exception as err:
            logger.error("get collection metadata failed %s", err)
            return None 


    def get_nft_from_api(self, nft_id: str) -> schemas.NftInfo:
        try:
            resp = requests.get(
                f"{self.api_url}/nfts/{nft_id}", 
                headers={"api-key": self.api_key})
            if resp.status_code not in [200, 201]:
                logger.info("refresh nft failed, resp: %s", resp.content)
                return None 
            return schemas.NftInfo.model_validate(resp.json())
        except Exception as err:
            logger.error("refresh nft status from api failed %s", err)
            return None 
    

    def get_updated_since(self, wallet: str, updated_timestamp: int) -> List[schemas.NftInfo]:
        try:
            params = {
                "since": updated_timestamp,
                "wallet": wallet,
            }
            resp = requests.post(
                f"{self.api_url}/updated", 
                headers={"api-key": self.api_key},
                json=params)
            if resp.status_code not in [200, 201]:
                logger.info("refresh nft failed, resp: %s", resp.content)
                return []
            return [schemas.NftInfo.model_validate(i) for i in resp.json()]
        except Exception as err:
            logger.error("refresh nft status from api failed %s", err)
            return []


    def submit_nft_to_api(self, nft: schemas.NftInfo) -> bool:
        try:
            resp = requests.post(
                f"{self.api_url}/nfts", 
                headers={"api-key": self.api_key},
                json=nft.model_dump(mode="json"))
            if resp.status_code not in [200, 201]:
                logger.info("submit nft failed, resp: %s", resp.content)
                return None 
            return resp.json().get("status") == "success"
        except Exception as err:
            logger.error("submit nft to api failed %s", err)
            return None 


settings = get_settings()
_CACHE_INSTANCE = NftApi(settings.nft_api_url,
                         settings.nft_api_key)

def get_nft_api():
    try:
        return _CACHE_INSTANCE
    except Exception as err:
        logger.error("get cache db failed %s", err)


NftApiDep = Annotated[NftApi, Depends(get_nft_api)]

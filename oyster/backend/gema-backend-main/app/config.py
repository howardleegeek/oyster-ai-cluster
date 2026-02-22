from functools import lru_cache

from typing_extensions import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import Depends


class Settings(BaseSettings):
    env: str = "DEV"
    db_host: str
    db_user: str
    db_passwd: str
    db_name: str
    db_pool_size: int
    redis_host: str
    redis_port: int
    redis_db: int
    # # jwt secret
    secret: str
    id_exp: int
    twitter_id: str
    twitter_secret: str
    twitter_redirect_url: str
    twitter_api_token: str
    sol_key: str
    sol_wallet: str
    mint_url: str
    alchemy_api_key: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    print("#########settings", Settings())
    s = Settings()
    return s


SettingsDep = Annotated[Settings, Depends(get_settings)]

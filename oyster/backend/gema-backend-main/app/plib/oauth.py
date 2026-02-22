import requests
import base64
import logging
from typing import Optional


logger = logging.getLogger("up")
TWITTER_OAUTH = "https://api.twitter.com/2/oauth2/token"
TWITTER_USER = "https://api.twitter.com/2/users/me"


def basic_auth(client_id: str, client_secret: str) -> str:
    content = f"{client_id}:{client_secret}"
    encoded = base64.urlsafe_b64encode(content.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


def twitter_oauth(
    client_id: str,
    client_secret: str,
    code: str,
    redirect_url: str
) -> Optional[str]:
    # return user twitter account
    logger.debug("client_id: %s", client_id)
    logger.debug("client secret: %s", client_secret)
    logger.debug("code: %s", code)
    logger.debug("redirect_url: %s", redirect_url)
    try:
        params = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_url,
            'code_verifier': 'challenge',
            'client_id': client_id,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': basic_auth(client_id, client_secret)
        }
        logger.debug("headers: %s", headers)
        logger.debug("params: %s", params)
        logger.debug("url: %s", TWITTER_OAUTH)
        resp = requests.post(TWITTER_OAUTH, headers=headers, params=params)
        if resp.status_code != 200:
            logger.error("calling twitter oauth failed %s", resp.status_code)
            logger.error("twitter response %s", resp.content)
            return None
        access_token = resp.json().get("access_token")
        if access_token is None:
            logger.error("no access token in oauth resp")
            return None
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        logger.debug("headers: %s", headers)
        logger.debug("url: %s", TWITTER_USER)
        resp = requests.get(TWITTER_USER, headers=headers)
        if resp.status_code != 200:
            logger.error("calling twitter user info failed %s",
                         resp.status_code)
            logger.error("twitter response %s", resp.content)
            return None
        data = resp.json()
        logger.debug("profile: %s", data)
        if data and data.get("data") and data.get("data").get("username"):
            return data.get("data").get("username")
        logger.info("oauth failed ")
        return None
    except Exception as err:
        logger.error("oauth failed %s", err)
        return None

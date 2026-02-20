import hashlib
import os
import requests
import base64
import logging
from typing import Optional, Tuple
from app.schemas.user import TwitterOauthResult


logger = logging.getLogger(__name__)


def generate_pkce_pair() -> Tuple[str, str]:
    """Generate a PKCE code_verifier and code_challenge pair.

    Returns:
        Tuple of (code_verifier, code_challenge) where:
        - code_verifier: a cryptographically random 43-128 character URL-safe string
        - code_challenge: the Base64-URL-encoded SHA256 hash of the code_verifier
    """
    # Generate 32 random bytes -> 43 base64url characters (within the 43-128 range)
    verifier_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(verifier_bytes).rstrip(b"=").decode("ascii")

    # S256: code_challenge = BASE64URL(SHA256(code_verifier))
    challenge_digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_digest).rstrip(b"=").decode("ascii")

    return code_verifier, code_challenge


TWITTER_OAUTH = "https://api.twitter.com/2/oauth2/token"
TWITTER_USER = "https://api.twitter.com/2/users/me?user.fields=profile_image_url"
TWITTER_FOLLOW = "https://api.twitter.com/2/users/{}/following"
TWITTER_DEFAULT_ICON = "https://pbs.twimg.com/profile_images/1922921964575821824/6LyVcddB_normal.jpg"


def basic_auth(client_id: str, client_secret: str) -> str:
    content = f"{client_id}:{client_secret}"
    encoded = base64.urlsafe_b64encode(content.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded}"


def twitter_oauth(
    client_id: str,
    client_secret: str,
    code: str,
    redirect_url: str,
    code_verifier: str = "challenge",
) -> Optional[TwitterOauthResult]:
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
            'code_verifier': code_verifier,
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
            if data.get("data").get("profile_image_url"):
                icon_url = data.get("data").get("profile_image_url")
            else:
                icon_url = TWITTER_DEFAULT_ICON

            return TwitterOauthResult(
                user_name=data.get("data").get("username"),
                user_id=data.get("data").get("id"),
                user_icon_url=icon_url,
                access_token=access_token)
        logger.info("oauth failed ")
        return None
    except Exception as err:
        logger.error("oauth failed %s", err)
        return None
    
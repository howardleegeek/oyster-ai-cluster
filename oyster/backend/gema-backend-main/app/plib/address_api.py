import requests
from pydantic import BaseModel
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger("up")


class Address(BaseModel):
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city_locality: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: str = "US"


@lru_cache(maxsize=256)
def parse_address(address: str, token: str) -> Optional[Address]:
    # Base URL for Shippo API endpoint
    base_url = "https://api.goshippo.com/v2/addresses/parse"
    # Authorization header with your API token
    headers = {
        "Authorization": f"ShippoToken {token}"
    }
    # Parameters for the request
    params = {"address": address}
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error(f"Error: {response.status_code}")
        return None
    try:
        result = response.json()
        logger.info("parse address %s", result)
        return Address(
            address_line_1=result.get("address_line_1"),
            address_line_2=result.get("address_line_2"),
            city_locality=result.get("city_locality"),
            state_province=result.get("state_province"),
            postal_code=result.get("postal_code"),
            country_code=result.get("country_code")
        )
    except Exception as err:
        logger.error(f"Error parsing address: {err}")
        return None


def validate_address(address: Address, token: str) -> bool:
    # Base URL for Shippo API endpoint
    base_url = "https://api.goshippo.com/v2/addresses/validate"
    headers = {
        "Authorization": f"ShippoToken {token}"
    }
    # Send GET request with headers and address data as JSON
    response = requests.get(base_url, headers=headers,
                            params=address.model_dump())
    if response.status_code != 200:
        logger.error(f"Error: {response.status_code}")
        return False
    try:
        # Get the validation response data in JSON format
        data = response.json()
        print(data)
        logger.info(f"Validation result: {data}")
        result = data["analysis"]["validation_result"]["value"]
        return result in ["valid", "partially_valid"]
    except Exception as err:
        logger.error("Error validating address: %s", err)
        return False

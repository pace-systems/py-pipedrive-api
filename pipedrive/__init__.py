"""
    Main API class.
"""
import os
from typing import Optional

from .deal import DealAPI
from .organization import OrganizationAPI
from .person import PersonAPI


class Pipedrive:
    """
    The Pipedrive API.
    """

    def __init__(self, subdomain: str, api_key: Optional[str] = None):
        if not subdomain:
            raise ValueError("Subdomain is required.")
        self.base_url = f"https://{subdomain}.pipedrive.com/api/v1/"
        if api_key is None:
            api_key = os.environ.get("PIPEDRIVE_API_KEY")
        self.api_key = api_key
        if not self.api_key:
            raise ValueError(
                "The API Key is required, pass api_key or "
                "set the PIPEDRIVE_API_KEY environment variable."
            )
        self.api_token = f"api_token={self.api_key}"
        self.deals = DealAPI(self)
        self.organizations = OrganizationAPI(self)
        self.people = PersonAPI(self)

    def __repr__(self):
        return f"Pipedrive('{self.base_url}')"

    def __str__(self):
        return self.__repr__()

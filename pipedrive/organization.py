"""
    Class to interact with the Pipedrive API for Organizations.
"""
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import requests

from pipedrive.mixins import FieldsMixin, URIMixin
from pipedrive.utils import process_response


class OrganizationAPI(  # pylint: disable=too-many-instance-attributes
    URIMixin,
    FieldsMixin
):
    """
    The Organization API.
    """

    def __init__(self, pipedrive):
        self.base_endpoint = "organizations"
        self.fields_endpoint = "organizationFields"
        self.search_endpoint = f"{self.base_endpoint}/search"
        self.pipedrive = pipedrive
        self.fields = None
        self._get_fields()
        self._details_cache = {}
        self._find_cache = {}
        self._people_cache = {}
        self._deals_cache = {}

    def _get_deals_uri(self, org_id, start: int = 0) -> str:
        """
        Get the deals endpoint URI.

        :param org_id: The Organization ID
        :param start: The starting offset

        :return: uri
        """
        return (
            f"{self.pipedrive.base_url}{self.base_endpoint}/{org_id}/deals?"
            f"start={start}&{self.pipedrive.api_token}"
        )

    def _get_people_uri(self, org_id, start: int = 0) -> str:
        """
        Get the people endpoint URI.

        :param org_id: The Organization ID
        :param start: The starting offset

        :return: uri
        """
        return (
            f"{self.pipedrive.base_url}{self.base_endpoint}/{org_id}/persons?"
            f"start={start}&{self.pipedrive.api_token}"
        )

    def _get_search_endpoint_uri(self, term, start: int = 0) -> str:
        """
        Get the search endpoint URI.

        :param term: the search term
        :param start: the starting offset

        :return: uri
        """
        quoted_term = quote(term)
        return (
            f"{self.pipedrive.base_url}{self.search_endpoint}?"
            f"term={quoted_term}&start={start}&{self.pipedrive.api_token}"
        )

    def get_details(self, org_id, no_cache: bool = False) -> Dict:
        """
        Get details about an organization.

        :param org_id:
        :param no_cache: Don't retrieve from cache

        :return:
        """
        if not no_cache:
            if org_id in self._details_cache:
                return self._details_cache[org_id]

        req = requests.get(self._get_details_uri(org_id))
        data = process_response(req)
        self._details_cache[org_id] = data
        return data

    def find(self, term, no_cache: bool = False) -> List:
        """
        Find an organization by search term.

        :param term: the search term
        :param no_cache: Don't retrieve from cache

        :return:
        """
        if not no_cache:
            cached_results = self._find_cache.get(term)
            if cached_results:
                return cached_results
        req = requests.get(self._get_search_endpoint_uri(term))
        data = process_response(req)
        value = data["items"]
        self._find_cache[term] = value
        return value

    def create_field(self, name, field_type: str = "varchar") -> None:
        """
        Create a new custom field for an organization.

        :param name: The name of the field
        :param field_type: The type of the field

        :return: None
        """
        payload = {
            "name": name,
            "field_type": field_type,
        }
        requests.post(self._get_fields_endpoint_uri(), data=payload)

    def create(self, name: str, address: str, visible_to: int = 3, **extra_fields):
        """
        Create a new organization.

        :param name: The name of the organization
        :param address: The address of the organization
        :param visible_to: Visibility of the organization
        :param extra_fields: Additional field values to add to the organization

        :return:
        """
        payload = {
            "name": name,
            "visible_to": visible_to,
            "address": address,
            **extra_fields,
        }
        req = requests.post(self._get_base_uri(), data=payload)
        return process_response(req)

    def get_people(self, organization_id, no_cache: bool = False) -> List:
        """
        Get all people associated with an organization.

        :param organization_id: The Organization ID
        :param no_cache: Don't retrieve from cache

        :return: List of People
        """
        if not no_cache:
            cached_people = self._people_cache.get(organization_id)
            if cached_people:
                return cached_people
        req = requests.get(self._get_people_uri(organization_id))
        data = process_response(req)
        self._people_cache[organization_id] = data
        return data

    def get_deals(self, organization_id, no_cache: bool = False) -> List:
        """
        Get all deals associated with an organization.

        :param organization_id: The Organization ID
        :param no_cache: Don't retrieve from cache

        :return: A List of Deals
        """
        if not no_cache:
            cached_deals = self._deals_cache.get(organization_id)
            if cached_deals:
                return cached_deals
        req = requests.get(self._get_deals_uri(organization_id))
        data = process_response(req)
        self._deals_cache[organization_id] = data
        return data

    def update(self, organization_id, fields: Dict) -> None:
        """
        Update an organization.

        :param organization_id: The Organization ID
        :param fields: fields to update

        :return: None
        """
        requests.put(self._get_details_uri(organization_id), data=fields)

    def filter_results(  # pylint: disable=too-many-arguments
        self,
        results,
        address_line_1,
        physical_address,
        physical_city,
        physical_state,
        physical_zip,
    ) -> Tuple[int, Dict]:
        """
        Filter results by address.

        :param results:
        :param address_line_1:
        :param physical_address:
        :param physical_city:
        :param physical_state:
        :param physical_zip:

        :return: An int score and likely object.
        """
        likely_match = None
        for result in results:
            item = result["item"]
            score = self._get_address_score(
                item["address"],
                physical_address,
                physical_city,
                physical_state,
                physical_zip,
            )
            if not score and item["name"] != address_line_1:
                continue
            if likely_match is None:
                likely_match = (score, item)
            else:
                likely_match: Tuple
                likely_score, _ = likely_match
                if score > likely_score:
                    likely_match = (score, item)
        return likely_match

    def _get_address_score(  # pylint: disable=too-many-arguments
        self, address, physical_address, physical_city, physical_state, physical_zip
    ) -> int:
        """
        Get the score of an address.

        :param address:
        :param physical_address:
        :param physical_city:
        :param physical_state:
        :param physical_zip:

        :return:
        """

        score = 0
        if address:
            phys_zip_in_address = physical_zip in address
            if phys_zip_in_address:
                score += 10
            phys_add_in_address = physical_address in address
            if phys_add_in_address:
                score += 5
            phys_city_in_address = physical_city in address
            if phys_city_in_address:
                score += 3
            phys_state_in_address = physical_state in address
            if phys_state_in_address:
                score += 2
        return score

    def filter_people_results(  # pylint: disable=too-many-arguments
        self, people, first_name, last_name, phone, email
    ):
        """
        Filter people results by name, phone, and email.

        :param people:
        :param first_name:
        :param last_name:
        :param phone:
        :param email:

        :return:
        """
        won_deals_found = False
        likely_match: Optional[Tuple] = None
        if people is None:
            return False, None
        lower_first_name = first_name.lower() if first_name else None
        lower_last_name = last_name.lower() if last_name else None
        lower_email = email.lower() if email else None

        for person in people:
            if person["won_deals_count"]:
                won_deals_found = True
            found_values = filter_person(
                person, lower_first_name, lower_last_name, lower_email, phone
            )
            score = get_person_score(*found_values)
            if not score or score < 7:
                continue
            if likely_match is None:
                likely_match = (score, person, *found_values)
            else:
                likely_match: Tuple
                if score > likely_match[0]:
                    likely_match = (score, person, *found_values)
        return won_deals_found, likely_match


def filter_person(
    person: Dict,
    lower_first_name: Optional[str],
    lower_last_name: Optional[str],
    lower_email: Optional[str],
    phone: Optional[str],
) -> Tuple[bool, bool, bool, bool]:
    """
    Filter a person by name, email, and phone.
    :param person:
    :param lower_first_name:
    :param lower_last_name:
    :param lower_email:
    :param phone:
    :return: Tuple of found values: (first, last, email, phone)
    """
    found_first_name = False
    found_last_name = False

    if (
        person["first_name"]
        and lower_first_name
        and lower_first_name in person["first_name"].lower()
    ):
        found_first_name = True
    if (
        person["last_name"]
        and lower_last_name
        and lower_last_name in person["last_name"].lower()
    ):
        found_last_name = True
    found_phone = person_has_phone(phone, person)
    found_email = person_has_email(lower_email, person)
    return found_first_name, found_last_name, found_email, found_phone


def person_has_phone(phone: str, person: Dict) -> bool:
    """
    Check if a person has the phone number.
    :param phone: A phone number.
        This is to avoid case sensitivity issues,
        but should not be done in this function to
        avoid excessive calls.
    :param person: A person response dict.
    :return: bool
    """
    for person_phone in person["phone"]:
        if person_phone["value"] == phone:
            return True
    return False


def person_has_email(email: str, person: Dict) -> bool:
    """
    Check if a person has an email.
    :param email: A *lowered* email address.
        This is to avoid case sensitivity issues,
        but should not be done in this function to
        avoid excessive calls.
    :param person: A person response dict.
    :return: bool
    """
    for person_email in person["email"]:
        if person_email["value"].lower() == email:
            return True
    return False


def get_person_score(
    found_first_name: bool, found_last_name: bool, found_email: bool, found_phone: bool
) -> int:
    """
    Get a score for a person.
    :param found_first_name:
    :param found_last_name:
    :param found_email:
    :param found_phone:
    :return:
    """
    score = 0
    if found_first_name:
        score += 7
    if found_last_name:
        score += 8
    if found_phone:
        score += 3
    if found_email:
        score += 4
    return score

"""
    Class to interact with the Pipedrive API for Person.
"""
from typing import List, Optional, Union

import requests

from pipedrive.mixins import FieldsMixin, URIMixin
from pipedrive.utils import process_response


class PersonAPI(URIMixin, FieldsMixin):
    """
    The Person API.
    """

    def __init__(self, pipedrive):
        self.base_endpoint = "persons"
        self.fields_endpoint = "personFields"
        self.pipedrive = pipedrive
        self.fields = None
        self._get_fields()

    def update(
        self,
        person_id,
        emails: Optional[Union[str, List]] = None,
        phones: Optional[Union[str, List]] = None,
        extra_fields: Optional[dict] = None,
    ):
        """
        Update a person.

        :param person_id: The ID of the person to update.
        :param emails: The email(s) of the person.
        :param phones: The phone(s) of the person.
        :param extra_fields: Extra fields to be updated on the person.

        :return:
        """
        if emails is None:
            emails = []
        if phones is None:
            phones = []
        if isinstance(emails, str):
            emails = [emails]
        if isinstance(phones, str):
            phones = [phones]

        payload = {
            "id": person_id,
            "email": emails,
            "phone": phones,
            **extra_fields,
        }

        req = requests.put(self._get_details_uri(person_id), data=payload)
        return process_response(req)

    def create(  # pylint: disable=too-many-arguments
        self,
        organization_id,
        first_name,
        last_name,
        email: Optional[Union[str, List]],
        phone: Optional[Union[str, List]],
        visible_to: int = 3,
        last_name_first: bool = False,
    ):
        """
        Create a new person.

        :param organization_id: The ID of the organization the person is tied to.
        :param first_name: The first name of the person.
        :param last_name: The last name of the person.
        :param email: The email(s) of the person.
        :param phone: The phone(s) of the person.
        :param visible_to: The visibility of the person.
        :param last_name_first: Display the last name first.

        :return:
        """
        if email and isinstance(email, str):
            email = [email]
        if phone and isinstance(phone, str):
            phone = [phone]

        payload = {
            "name": f"{last_name}, {first_name}"
            if last_name_first
            else f"{first_name} {last_name}",
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "org_id": organization_id,
            "visible_to": visible_to,
        }
        req = requests.post(self._get_base_uri(), data=payload)
        return process_response(req)

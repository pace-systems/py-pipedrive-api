"""
    Class to interact with the Pipedrive API for Deals.
"""
from typing import Dict, List, Optional

import requests

from pipedrive.mixins import FieldsMixin, URIMixin
from pipedrive.utils import append_params, process_response


class DealAPI(URIMixin, FieldsMixin):
    """
    The Deal API.
    """

    def __init__(self, pipedrive):
        self.base_endpoint = "deals"
        self.fields_endpoint = "dealFields"
        self.deal_endpoint = f"{self.base_endpoint}/"
        self.pipedrive = pipedrive
        self.fields = None
        self._get_fields()

    def create(self, organization_id, person_id, title: str, **extra_fields):
        """
        Create a new deal.

        :param organization_id: The ID of the organization the deal is tied to.
        :param person_id: The ID of the person the deal is tied to.
        :param title:  The title of the deal
        :param extra_fields: Extra fields to be added to the deal.

        :return:
        """
        payload = {
            "org_id": organization_id,
            "person_id": person_id,
            "title": title,
            **extra_fields,
        }
        req = requests.post(self._get_base_uri(), data=payload)
        return process_response(req)

    def update_deal(self, deal_id, fields: Dict) -> None:
        """
        Update a deal.

        :param deal_id: The ID of the deal to update.
        :param fields: The fields to update.

        :return:
        """
        requests.put(self._get_details_uri(deal_id), data=fields)

    def get_all(  # pylint: disable=too-many-arguments
        self,
        filter_id: Optional[int] = None,
        stage_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        owned_by_you: Optional[int] = None,  # 0 or 1
    ) -> Optional[List]:
        """
        Get all deals.

        :param filter_id: The ID of the filter to use
        :param stage_id: If supplied, only deals within the given
            stage will be returned
        :param user_id: If supplied, only deals matching the
            given user will be returned. However, filter_id
            and owned_by_you takes precedence over user_id when
            supplied.
        :param status: Only fetch deals with a specific status.
            If omitted, all not deleted deals are fetched.

            DEFAULT all_not_deleted
            VALUES   open    won     lost    deleted     all_not_deleted
        :param start: Pagination start
        :param limit: Items shown per page
        :param sort: The field names and sorting mode separated by a
            comma (field_name_1 ASC, field_name_2 DESC). Only
             first-level field keys are supported (no nested keys).
        :param owned_by_you: When supplied, only deals owned by you
            are returned. However, filter_id takes precedence over
             owned_by_you when both are supplied.
            VALUES  0   1

        :return:
        """

        uri = self._get_base_uri()
        params = {
            "filter_id": filter_id,
            "stage_id": stage_id,
            "user_id": user_id,
            "status": status,
            "start": start,
            "limit": limit,
            "sort": sort,
            "owned_by_you": owned_by_you,
        }
        uri = append_params(uri, params, True)
        req = requests.get(uri)
        return process_response(req)

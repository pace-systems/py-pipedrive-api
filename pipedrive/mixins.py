"""
    Mixin classes for Pipedrive API
"""
import requests


class URIMixin:  # pylint: disable=too-few-public-methods
    """
       Provides generic methods for building URIs
    """

    def _get_base_uri(self) -> str:
        """
        Get the base URI for the endpoint.

        :return: URI
        """
        return (
            f"{self.pipedrive.base_endpoint}/{self.base_endpoint}?"
            f"{self.pipedrive.api_token}"
        )

    def _get_fields_endpoint_uri(self) -> str:
        """
        Get the URI for the fields endpoint.

        :return: URI
        """
        return (
            f"{self.pipedrive.base_url}{self.fields_endpoint}?"
            f"{self.pipedrive.api_token}"
        )

    def _get_details_uri(self, obj_id) -> str:
        """
        Get the details endpoint URI.

        :param obj_id: The Object ID

        :return: uri
        """
        return (
            f"{self.pipedrive.base_url}{self.base_endpoint}/{obj_id}?"
            f"{self.pipedrive.api_token}"
        )


class FieldsMixin:
    """
    Provides a generic way to work with custom fields for each API.
    """

    # TODO: Make this stuff an interface.  # pylint: disable=fixme
    # fields = {}

    # def _get_fields_endpoint_uri(self) -> str:
    #    raise NotImplementedError()

    def _get_fields(self, no_cache: bool = False):
        """
        Get the fields for the API and caches them.

        :param no_cache: Don't retrieve from cache

        :return:
        """
        if self.fields and not no_cache:
            return self.fields
        req = requests.get(self._get_fields_endpoint_uri())
        json_data = req.json()
        if not json_data["success"]:
            return None
        self.fields = json_data["data"]
        self.fields_by_key = {field["key"]: field for field in json_data["data"]}
        self.fields_by_name = {
            field["name"].lower(): field for field in json_data["data"]
        }
        return self.fields

    def get_field_by_name(self, name: str):
        """
        Get a cached field by its name.

        :param name: The name

        :return: A field, maybe.
        """
        name = name.lower()
        return self.fields_by_name.get(name)

    def get_field_by_key(self, key: str):
        """
        Get a cached field by its key.

        :param key: The key

        :return: A field, maybe.
        """
        return self.fields_by_key.get(key)

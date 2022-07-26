"""
    Utility Functions
"""
from typing import Dict, List, Optional, Union


def process_response(response) -> Optional[Union[Dict, List]]:
    """
    Processes the response from the API and returns a dictionary.

    :param response: The response from the API.

    :return: A dictionary or list, maybe.
    """
    if response.status_code == 200:
        json_data = response.json()
    else:
        raise Exception(response.text)

    if "success" in json_data and json_data["success"]:
        return json_data["data"]
    if "status" in json_data and not json_data["status"]:
        raise Exception(json_data["error"])
    return None


def append_params(uri, params, not_first=False):
    """
    Appends parameters to a URI.

    :param uri: The URI
    :param params: The parameters
    :param not_first: Start with ? or &

    :return: URI with parameters
    """
    first_param = not not_first
    for key, value in params.items():
        if value and first_param:
            uri += f"?{key}={value}"
            first_param = False
        elif value:
            uri += f"&{key}={value}"
    return uri

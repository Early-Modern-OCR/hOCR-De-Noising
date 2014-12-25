import json
import logging
import requests
from urlparse import urljoin

logger = logging.getLogger('emop')


class EmopAPI(object):

    def __init__(self, url_base, api_headers):
        """ Initialize EmopAPI object and attributes

        Args:
            url_base (str): Base of the API URL.
                Example: "http://emop-dashboard.tamu.edu"
            api_headers (dict): The HTTP headers to use for API
                requests such as Content-Type and Authorization.
        """
        self.url_base = url_base
        self.api_headers = api_headers

    def get_request(self, url_path, params={}):
        """Sends a GET request

        Send a GET request with optional params to
        the emop-dashboard.

        Args:
            url_path (str): The API URL path excluding hostname.
            params (dict, optional): Params to send with GET request.

        Returns:
            dict: The request's JSON response data.
        """
        json_data = {}
        full_url = urljoin(self.url_base, url_path)
        logger.debug("Sending GET request to %s" % full_url)
        if params:
            logger.debug("GET request params: %s" % str(params))
        get_r = requests.get(full_url, params=params, headers=self.api_headers)

        if get_r.status_code == requests.codes.ok:
            json_data = get_r.json()
        else:
            logger.error("GET %s failed with error code %s" % (full_url, get_r.status_code))
        return json_data

    def put_request(self, url_path, data={}):
        """Sends a PUT request

        Send a PUT request to the emop-dashboard.

        Args:
            url_path (str): The API URL path excluding hostname.
            data (dict, optional): The data to send with PUT request.

        Returns:
            dict: The request's JSON response data.
        """
        json_data = {}
        full_url = urljoin(self.url_base, url_path)
        logger.debug("Sending PUT request to %s" % full_url)
        if data:
            logger.debug("PUT request data: %s" % str(data))
        put_r = requests.put(full_url, data=json.dumps(data), headers=self.api_headers)

        if put_r.status_code == requests.codes.ok:
            json_data = put_r.json()
        else:
            logger.error("GET %s failed with error code %s" % (full_url, put_r.status_code))
        return json_data

import json
import logging
import requests
from urlparse import urljoin

logger = logging.getLogger('emop')


class EmopAPI(object):

    def __init__(self, url_base, api_headers):
        self.url_base = url_base
        self.api_headers = api_headers

    def get_request(self, url_path, params=None):
        full_url = urljoin(self.url_base, url_path)
        get_r = requests.get(full_url, params=params, headers=self.api_headers)

        if get_r.status_code == requests.codes.ok:
            json_data = get_r.json()
            return json_data
        else:
            logger.error("GET %s failed with error code %s" % (full_url, get_r.status_code))
            return None

    def put_request(self, url_path, data=None):
        full_url = urljoin(self.url_base, url_path)
        put_r = requests.put(full_url, data=json.dumps(data), headers=self.api_headers)

        if put_r.status_code == requests.codes.ok:
            json_data = put_r.json()
            return json_data
        else:
            logger.error("GET %s failed with error code %s" % (full_url, put_r.status_code))
            return None

# Copyright 2015 Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import syntribos.checks.http as http_checks
from syntribos.clients.http.base_http_client import HTTPClient


class SynHTTPClient(HTTPClient):

    """This is the basic HTTP client used by Syntribos.

    It aliases `send_request` to `request` so logging/exception handling is
    done in one place, for all requests. Also checks for bad HTTP status codes
    and adds a signal if one is found.
    """

    def request(self, method, url, headers=None, params=None, data=None,
                sanitize=False, requestslib_kwargs=None):
        """Sends a request (passes to `requests.request`)

        :param str method: Request method
        :param str url: URL to request
        :param dict headers: Dictionary of headers in name:value format
        :param dict params: Dictionary of params in name:value format
        :param dict data: Data to send as part of request body
        :param dict requestslib_kwargs: Keyword arguments to pass to requests
        :returns: tuple of (response, signals)
        """
        if not requestslib_kwargs:
            requestslib_kwargs = {"timeout": 10}
        elif not requestslib_kwargs.get("timeout", None):
            requestslib_kwargs["timeout"] = 10

        response, signals = super(SynHTTPClient, self).request(
            method, url, headers=headers, params=params, data=data,
            sanitize=sanitize,
            requestslib_kwargs=requestslib_kwargs)

        if response is not None:
            signals.register(http_checks.check_status_code(response))
            signals.register(http_checks.check_content_type(response))

        return (response, signals)

    def send_request(self, request_obj):
        """This sends a request based on a RequestOjbect.

        RequestObjects are generated by a parser (e.g.
        :class:`syntribos.clients.http.parser.RequestCreator`) from request
        template files, and passed to this method to send the request.

        :param request_obj: A RequestObject generated by a parser
        :type request_obj: :class:`syntribos.clients.http.models.RequestObject`
        :returns: tuple of (response, signals)
        """
        response, signals = self.request(
            request_obj.method, request_obj.url,
            headers=request_obj.headers, params=request_obj.params,
            data=request_obj.data, sanitize=request_obj.sanitize)

        return (response, signals)
import datetime
import sys
import time
import httplib
try:
    import json as simplejson  # For Python 2.6
except ImportError:
    import simplejson
from urlparse import urlparse, urlunparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs
from urllib import urlencode

GITHUB_URL = "https://github.com"

URL_PREFIX = "https://github.com/api/v2/json"


class GithubError(Exception):
    """An error occured when making a request to the Github API."""


class GithubRequest(object):
    github_url = GITHUB_URL
    url_format = "%(github_url)s/api/%(api_version)s/%(api_format)s"
    api_version = "v2"
    api_format = "json"
    GithubError = GithubError

    connector_for_scheme = {
        "http": httplib.HTTPConnection,
        "https": httplib.HTTPSConnection,
    }

    def __init__(self, username=None, api_token=None, url_prefix=None,
            debug=False, requests_per_second=None, access_token=None):
        """
        Make an API request.
        """
        self.username = username
        self.api_token = api_token
        self.access_token = access_token
        self.url_prefix = url_prefix
        self.debug = debug
        if requests_per_second is None:
            self.delay = 0
        else:
            self.delay = 1.0 / requests_per_second
        self.last_request = datetime.datetime(1900, 1, 1)
        if not self.url_prefix:
            self.url_prefix = self.url_format % {
                "github_url": self.github_url,
                "api_version": self.api_version,
                "api_format": self.api_format,
            }

    def encode_authentication_data(self, extra_post_data):
        if self.access_token:
            post_data = {"access_token": self.access_token}
        elif self.username and self.api_token:
            post_data = {"login": self.username,
                         "token": self.api_token}
        else:
            post_data = {}
        post_data.update(extra_post_data)
        return urlencode(dict([k, v.encode('utf-8')] for k, v in post_data.items()))

    def get(self, *path_components):
        path_components = filter(None, path_components)
        return self.make_request("/".join(path_components))

    def post(self, *path_components, **extra_post_data):
        path_components = filter(None, path_components)
        return self.make_request("/".join(path_components), extra_post_data,
            method="POST")

    def make_request(self, path, extra_post_data=None, method="GET"):
        if self.delay:
            since_last = (datetime.datetime.now() - self.last_request)
            since_last_in_seconds = (since_last.days * 24 * 60 * 60) + since_last.seconds + (since_last.microseconds/1000000.0)
            if since_last_in_seconds < self.delay:
                duration = self.delay - since_last_in_seconds
                if self.debug:
                    sys.stderr.write("delaying API call %s\n" % duration)
                time.sleep(duration)

        extra_post_data = extra_post_data or {}
        url = "/".join([self.url_prefix, path])
        result = self.raw_request(url, extra_post_data, method=method)

        if self.delay:
            self.last_request = datetime.datetime.now()
        return result

    def raw_request(self, url, extra_post_data, method="GET"):
        scheme, netloc, path, params, query, fragment = urlparse(url)
        hostname = netloc.split(':')[0]
        post_data = None
        headers = self.http_headers
        headers["Accept"] = "text/html"
        method = method.upper()
        if extra_post_data or method == "POST":
            post_data = self.encode_authentication_data(extra_post_data)
            headers["Content-Length"] = str(len(post_data))
        else:
            path = urlunparse((scheme, netloc, path, params,
                self.encode_authentication_data(parse_qs(query)),
                fragment))
        connector = self.connector_for_scheme[scheme]
        connection = connector(hostname)
        connection.request(method, path, post_data, headers)
        response = connection.getresponse()
        response_text = response.read()
        if self.debug:
            sys.stderr.write("URL:[%s] POST_DATA:%s RESPONSE_TEXT: [%s]\n" % (
                                path, post_data, response_text))
        if response.status >= 400:
            raise RuntimeError("unexpected response from github.com %d: %r" % (
                               response.status, response_text))
        json = simplejson.loads(response_text)
        if json.get("error"):
            raise self.GithubError(json["error"][0]["error"])

        return json

    @property
    def http_headers(self):
        return {"User-Agent": "pygithub2 v1",
                "Accept-Encoding": "application/json"}

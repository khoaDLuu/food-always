"""
Use the requests library to crawl the text content from the html of the provided URL
"""

import requests
from django.conf import settings
from fake_useragent import UserAgent


class HTMLGetError(Exception):
    pass


class ProxiesIsEmpty(Exception):
    pass


# Instantiate a user agent
_useragent = UserAgent()


def get_html_text(url, ua=_useragent, refer_page=None, tag=True, stream=False):
    """
    Try to get a web page information, and return the page data
    Params:
        ua: user agent
        refer_page: source page
        tag: Get the webpage by default, False means the obtained picture (binary data)
        stream: param for requests
    """

    headers = {
        "User-Agent": ua.random,
    }
    # If there is a reference page, add it to the request header
    if refer_page:
        headers["Referer"] = refer_page

    # Proxy server
    proxyHost = settings.PROXY_HOST
    proxyPort = settings.PROXY_PORT
    # Proxy tunnel verification information
    proxyUser = settings.PROXY_USER
    proxyPass = settings.PROXY_PSWD
    # Build agent
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    try:
        r = requests.get(url=url, headers=headers, proxies=proxies, timeout=10, stream=stream)
        r.raise_for_status()
        r.encoding = "utf-8"
    except Exception as e:
        # Generally it is an error caused by the agent being blocked
        error_info = (
            "An error occurred while getting the webpage, please check...\n"
            "Error message: {0}".format(e)
        )
        raise HTMLGetError(error_info)

    if tag:
        return r.text
    else:
        return r


# Simple crawler program, used for crawling test of a single page without proxy
def get_html_text_sample(url, ua=_useragent):
    headers = {
        "User-Agent": ua.random,
    }
    try:
        with requests.get(url=url, headers=headers, timeout=30) as r:
            r.raise_for_status()
            r.encoding = "utf-8"
    except Exception as e:
        error_info = (
            "An error occurred while getting the webpage, please check...\n"
            "Error message: {0}".format(e)
        )
        raise HTMLGetError(error_info)
    else:
        return r.text


def create_headers(ua=_useragent):
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us",
        "Connection": "keep-alive",
        "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
    }

    proxyHost = "proxyHost"
    proxyPort = "proxyPort"
    proxyUser = "proxyUser"
    proxyPass = "proxyPass"
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    return headers, proxies

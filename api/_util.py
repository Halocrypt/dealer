from random import choice

import requests

from ._constants import (
    AVAILABLE,
    DEALER_KEY,
    REMOVE_REQUEST_HEADERS,
    REMOVE_RESPONSE_HEADERS,
)


def get_host():
    return choice(AVAILABLE)


def others(x):
    return [host for host in AVAILABLE if host != x]


def invalidate(keys, current):
    other_hosts = others(current)
    for i in other_hosts:
        requests.post(
            f"https://{i}/admin/-/invalidate/",
            headers={"x-access-key": DEALER_KEY},
            json={"keys": keys},
        )


def lower_dict(d):
    return {k.lower(): v for k, v in dict(d).items()}


def remove_headers(h, source):
    for i in source:
        h.pop(i, None)

    return h


def process_request_headers(x):
    return remove_headers(lower_dict(x), REMOVE_REQUEST_HEADERS)


def process_response_headers(x):
    return remove_headers(lower_dict(x), REMOVE_RESPONSE_HEADERS)


def calc_time(end, start):
    if any(x is None for x in (end, start)):
        return None
    return round(end - start, 4)

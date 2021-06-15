from json import dumps, loads
from time import time

import requests
from flask import Flask, Response, request

from ._constants import DEALER_KEY, EXPOSE_HEADERS, METHODS, OPTIONS_RESPONSE
from ._util import (
    calc_time,
    get_host,
    invalidate,
    process_request_headers,
    process_response_headers,
)

app = Flask(__name__)




@app.route("/", methods=METHODS)
@app.route("/<path:p>", methods=METHODS)
def catch_all(p=""):
    where = get_host()
    method = request.method.lower()
    if method == "options":
        return OPTIONS_RESPONSE
    url = f"https://{where}/{p}"

    func = getattr(requests, method)

    data = request.get_data()
    headers = process_request_headers(request.headers)
    response: requests.Response

    func_start_time = time()
    response = func(url, headers={**headers, "x-access-key": DEALER_KEY}, data=data)
    proxy_end_time = time()

    response_headers = process_response_headers(response.headers)

    invalidate_keys = response_headers.get("x-invalidate")

    did_invalidate = invalidate_keys is not None

    invalidation_start_time = invalidation_end_time = None
    if did_invalidate:
        invalidation_start_time = time()
        invalidate(loads(invalidate_keys), where)
        invalidation_end_time = time()
    func_end_time = time()

    debug_info = {
        "dealt_to": where,
        "cache_hit": response_headers.get("x-cached-response"),
        "did_invalidate": invalidate_keys,
        "proxy_time": calc_time(proxy_end_time, func_start_time),
        "invalidation_time": calc_time(invalidation_end_time, invalidation_start_time),
        "total_time": calc_time(func_end_time, func_start_time),
    }
    return Response(
        response.content,
        headers={
            "x-debug": dumps(debug_info),
            **response_headers,
        },
        status=response.status_code,
    )


@app.errorhandler(500)
def error_handler(e):
    return {"error": "An unknown error occured", "tb": f"{e}"}


@app.after_request
def cors(resp):
    resp.headers["access-control-allow-origin"] = request.headers.get("origin", "*")
    resp.headers["access-control-allow-headers"] = request.headers.get(
        "access-control-request-headers", "*"
    )
    resp.headers["access-control-allow-credentials"] = "true"
    resp.headers["access-control-max-age"] = "86400"
    resp.headers["access-control-expose-headers"] = EXPOSE_HEADERS
    resp.headers[
        "access-control-allow-methods"
    ] = "GET, POST, PATCH, PUT, OPTIONS, DELETE"

    return resp


if __name__ == "__main__":
    app.run(debug=True)

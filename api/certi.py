from time import time

import requests
from flask import Flask, Response, request

from ._constants import OPTIONS_RESPONSE
from ._util import (
    calc_time,
    process_response_headers,
)

app = Flask(__name__)


@app.route("/cert/proxy/<file>")
def certi(file):
    method = request.method.lower()
    if method == "options":
        return OPTIONS_RESPONSE
    url = f"https://h2.halocrypt.com/certificates/{file}"
    start = time()
    resp = requests.get(url)
    end = time()
    response_headers = process_response_headers(resp.headers)
    debug = {"orig_url": url, "proxy-time": calc_time(end, start)}
    return Response(
        resp.content,
        headers={
            "content-type": response_headers.get(
                "content-type", "application/octet-stream"
            ),
            "x-debug": debug,
            "Cache-Control": "s-maxage=31536000",
        },
    )


@app.after_request
def cors(resp):
    resp.headers["access-control-allow-origin"] = "*"
    resp.headers["access-control-max-age"] = "86400"
    resp.headers[
        "access-control-allow-methods"
    ] = "GET, POST, PATCH, PUT, OPTIONS, DELETE"

    return resp

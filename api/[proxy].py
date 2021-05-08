# Ported from https://github.com/marcopolee/hookbot/blob/master/index.js


import requests
from flask import Flask, request, Response
from random import choice
from json import dumps, loads
from threading import Thread
import os

app = Flask(__name__)

methods = ["get", "post", "patch", "put", "delete"]

available = ["s1.halocrypt.com", "s2.halocrypt.com", "s3.halocrypt.com"]


def get_host():
    return choice(available)


def others(x):
    return [host for host in available if host != x]


def invalidate(keys, current):
    other_hosts = others(current)
    threads = []
    for i in other_hosts:
        thread = Thread(
            target=requests.post,
            args=(f"https://{i}/admin/-/invalidate/"),
            kwargs={"json": keys},
        )
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()


_REMOVE_HEADERS = (
    "x-forwarded-host",
    "x-forwarded-for",
    "host",
    "accept-encoding",
    "x-vercel-deployment-url",
    "x-vercel-id",
    "x-vercel-forwarded-for",
    "x-vercel-trace",
)


def lower_dict(d):
    return {k.lower(): v for k, v in dict(d).items()}


def remove_headers(h):
    for i in _REMOVE_HEADERS:

        h.pop(i, None)

    return h


DEALER_KEY = os.environ["DEALER_KEY"]


@app.route("/", methods=methods)
@app.route("/<path:p>", methods=methods)
def catch_all(p=""):
    where = get_host()
    method = request.method.lower()
    url = f"https://{where}/{p}"

    func = getattr(requests, method)

    data = request.get_data()
    headers = remove_headers(lower_dict(request.headers))
    response: requests.Response

    response = func(url, headers={**headers, "x-access-key": DEALER_KEY}, data=data)
    response_headers = response.headers
    response_headers.pop("content-encoding", None)
    invalidate_keys = response_headers.get("x-invalidate")
    did_invalidate = invalidate_keys is not None

    if did_invalidate:
        invalidate(loads(invalidate_keys), where)
    debug_info = {
        "dealt-to": where,
        "cache-hit": response_headers.get("x-cached-response"),
        "did-invalidate": did_invalidate,
    }
    return Response(
        response.content,
        headers={
            "x-debug": dumps(debug_info),
            **response_headers,
        },
        status=response.status_code,
    )


EXPOSE_HEADERS = ", ".join(("x-access-token", "x-refresh-token", "x-dynamic"))


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

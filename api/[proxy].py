# Ported from https://github.com/marcopolee/hookbot/blob/master/index.js


import requests
from flask import Flask, request, Response
from random import choice
from json import dumps, loads
from threading import Thread

app = Flask(__name__)

methods = ["get", "post", "patch", "put", "delete"]

available = ["s.1.halocrypt.com", "s.2.halocrypt.com", "s.3.halocrypt.com"]


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


@app.route("/", methods=methods)
@app.route("/<path:p>", methods=methods)
def catch_all(p=""):
    where = get_host()
    method = request.method.lower()
    url = f"https://httpbin.org/{method}" or f"https://{where}/{p}"

    func = getattr(requests, method)

    data = request.get_data()
    headers = request.headers
    response: requests.Response

    response = func(url, headers=headers, data=data)
    response_headers = response.headers
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
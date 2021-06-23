from os import environ
from flask import Response

DEALER_KEY = environ["DEALER_KEY"]
FALLBACK = environ.get("FALLBACK")

METHODS = ["get", "post", "patch", "put", "delete"]

AVAILABLE = (
    ["halo21.herokuapp.com"]
    if FALLBACK == "1"
    else ["s1.halocrypt.com"]
)


REMOVE_REQUEST_HEADERS = (
    "x-forwarded-host",
    "x-forwarded-for",
    "host",
    "accept-encoding",
    "x-vercel-deployment-url",
    "x-vercel-id",
    "x-vercel-forwarded-for",
    "x-vercel-trace",
)
REMOVE_RESPONSE_HEADERS = ("content-encoding", "via", "alt-svc")
EXPOSE_HEADERS = ", ".join(("x-access-token", "x-refresh-token", "x-dynamic"))
OPTIONS_RESPONSE = Response("", status=200, headers={"x-debug": "BYPASS"})

from os import environ

METHODS = ["get", "post", "patch", "put", "delete"]

AVAILABLE = ["s1.halocrypt.com", "s2.halocrypt.com", "s3.halocrypt.com"]


DEALER_KEY = environ["DEALER_KEY"]

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

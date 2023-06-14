import os

from cybsi.cloud import APIKeyAuth, Client, Config, Limits, Timeouts

if __name__ == "__main__":
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")

    auth = APIKeyAuth(api_url=api_url, api_key=api_key)

    # Set custom timeouts and limits of HTTP client
    limits = Limits(max_connections=100, max_keepalive_connections=20)
    timeouts = Timeouts(default=3.0)

    config = Config(api_url, auth, ssl_verify=False, timeouts=timeouts, limits=limits)
    client = Client(config)
    # then use client as usual

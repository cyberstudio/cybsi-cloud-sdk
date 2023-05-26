from os import environ

from cybsi.cloud import APIKeyAuth, Config, Client, Limits, Timeouts

if __name__ == "__main__":
    api_key = environ["CCL_API_KEY"]
    api_url = environ["CCL_API_URL"]

    auth = APIKeyAuth(api_url=api_url, api_key=api_key)

    # Set custom timeouts and limits of HTTP client
    limits = Limits(max_connections=100, max_keepalive_connections=20)
    timeouts = Timeouts(default=3.0)

    config = Config(api_url, auth, ssl_verify=False, timeouts=timeouts, limits=limits)
    client = Client(config)
    client.iocean

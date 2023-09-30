from cybsi.cloud import Client, Config, Limits, Timeouts

if __name__ == "__main__":
    # Set custom timeouts and limits of HTTP client
    limits = Limits(max_connections=100, max_keepalive_connections=20)
    timeouts = Timeouts(default=3.0)
    config = Config(
        api_key="the cryptic string", ssl_verify=False, timeouts=timeouts, limits=limits
    )
    client = Client(config)
    # then use client as usual

#!/usr/bin/env python3
from cybsi.cloud import APIKeyAuth, Config, Client
from cybsi.cloud.pagination import Page, chain_pages

if __name__ == "__main__":
    api_url = "https://cybsi.cloud"
    auth = APIKeyAuth(api_url=api_url, api_key="api_key")
    config = Config(api_url, auth)

    start_page: Page[T] # FIXME: Use Iocean Object Type

    with Client(config) as client:
        start_page, _ = client.iocean.collections.get()  # FIXME implement get()
        for item in chain_pages(start_page):
            # Do something with an item
            pass

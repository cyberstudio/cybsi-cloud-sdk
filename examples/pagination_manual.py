#!/usr/bin/env python3
from cybsi.cloud import APIKeyAuth, Client, Config
from cybsi.cloud.pagination import Page

if __name__ == "__main__":
    api_url = "https://cybsi.cloud"
    auth = APIKeyAuth(api_url=api_url, api_key="api_key")
    config = Config(api_url, auth)

    page: Page[object]  # FIXME: provide type

    with Client(config) as client:
        page, _ = client.iocean.collections.get()  # FIXME: implement get()
        while page:
            # Page is iterable
            for el in page:
                # Do something with element
                pass
            # Do something with a page
            page = page.next_page()  # type: ignore

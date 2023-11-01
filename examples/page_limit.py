#!/usr/bin/env python3
from typing import Optional

from cybsi.cloud import Client, Config
from cybsi.cloud.auth import ResourceView
from cybsi.cloud.pagination import Page

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        page: Optional[Page[ResourceView]] = client.auth.resources.filter(limit=3)
        while page:
            # Got page with maximum of 3 elements
            # Page is iterable
            for item in page:
                # Do something with an item
                pass
            # Fetch next page
            page = page.next_page()

#!/usr/bin/env python3
from typing import Optional

from cybsi.cloud import Client, Config
from cybsi.cloud.iocean import CollectionCommonView
from cybsi.cloud.pagination import Page

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        page: Optional[Page[CollectionCommonView]] = client.iocean.collections.filter()
        while page:
            # Page is iterable
            for item in page:
                # Do something with an item
                pass
            # Fetch next page
            page = page.next_page()

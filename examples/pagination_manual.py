#!/usr/bin/env python3
import os
from typing import Optional

from cybsi.cloud import Client, Config
from cybsi.cloud.iocean import CollectionCommonView
from cybsi.cloud.pagination import Page

if __name__ == "__main__":
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")
    config = Config(api_url, api_key)

    with Client(config) as client:
        page: Optional[Page[CollectionCommonView]] = client.iocean.collections.filter()
        while page:
            # Page is iterable
            for item in page:
                # Do something with an item
                pass
            # Fetch next page
            page = page.next_page()

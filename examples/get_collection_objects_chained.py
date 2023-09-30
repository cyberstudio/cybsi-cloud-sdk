#!/usr/bin/env python3
from cybsi.cloud import Client, Config
from cybsi.cloud.pagination import chain_pages

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        collection_id = "example-collection"
        start_page, _ = client.iocean.objects.filter(
            collection_id=collection_id,
        )
        for item in chain_pages(start_page):
            # Do something with an item
            pass

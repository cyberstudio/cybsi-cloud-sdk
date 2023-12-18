#!/usr/bin/env python3
from cybsi.cloud import Client, Config
from cybsi.cloud.pagination import chain_pages

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        # Retrieve first page of enrichment result object schemas.
        start_page = client.insight.schemas.filter()

        for schema in chain_pages(start_page):
            # Do something with the schema as SchemaCommonView.
            print(schema)

#!/usr/bin/env python3
from cybsi.cloud import Client, Config
from cybsi.cloud.pagination import chain_pages

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        collection_id = "phishing"

        # Retrieve collection schema, it describes all attributes
        # of objects you can encounter in the collection.
        schema_view = client.iocean.collections.view_schema(
            collection_id=collection_id)
        print(schema_view.schema)

        # Retrieve first page of collection objects.
        start_page, _ = client.iocean.objects.filter(
            collection_id=collection_id,
        )

        for obj in chain_pages(start_page):
            # Do something with the object.
            print(obj)

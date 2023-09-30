#!/usr/bin/env python3
from cybsi.cloud import Client, Config
from cybsi.cloud.iocean.objects import ObjectKeyType

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")
    client = Client(config)

    collection_id = "example-collection"
    client.iocean.objects.delete(
        collection_id=collection_id,
        key_type=ObjectKeyType.MD5Hash,
        key_value="cea239ce075fcb2151ce9ee10227f042",
    )

    client.close()

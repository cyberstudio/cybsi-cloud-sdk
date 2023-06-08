#!/usr/bin/env python3
import os

from cybsi.cloud import APIKeyAuth, Client, Config
from cybsi.cloud.iocean.objects import ObjectKeyType

if __name__ == "__main__":
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")
    auth = APIKeyAuth(api_url=api_url, api_key=api_key)
    config = Config(api_url, auth)
    client = Client(config)

    collection_id = "example-collection"
    client.iocean.objects.delete(
        collection_id=collection_id,
        key_type=ObjectKeyType.MD5Hash,
        key_value="cea239ce075fcb2151ce9ee10227f042",
    )

    client.close()

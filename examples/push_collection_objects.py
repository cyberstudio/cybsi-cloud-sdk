#!/usr/bin/env python3
import os
from hashlib import md5

from cybsi.cloud import APIKeyAuth, Client, Config
from cybsi.cloud.iocean.objects import ObjectKeyType, ObjectType

if __name__ == "__main__":
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")
    auth = APIKeyAuth(api_url=api_url, api_key=api_key)
    config = Config(api_url, auth)
    client = Client(config)

    collection_id = "example-collection"
    for i in range(1000):
        hash = md5(str(i).encode("ascii")).hexdigest()
        keys = [(ObjectKeyType.MD5Hash, hash)]
        context = {"size": i + 1}
        client.iocean.objects.add(
            collection_id=collection_id,
            obj_type=ObjectType.File,
            keys=keys,
            context=context,
        )

    client.close()

#!/usr/bin/env python3
import asyncio
import os
from hashlib import md5

from cybsi.cloud import AsyncClient, Config
from cybsi.cloud.iocean.objects import ObjectKeyType, ObjectType


async def main():
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")
    config = Config(api_url, api_key)

    collection_id = "example-collection"
    async with AsyncClient(config) as client:
        objects = (
            client.iocean.objects.add(
                collection_id=collection_id,
                obj_type=ObjectType.File,
                keys=[(ObjectKeyType.MD5Hash, md5(str(i).encode("ascii")).hexdigest())],
                context={"size": i + 1},
            )
            for i in range(1000)
        )
        await asyncio.gather(*objects)


if __name__ == "__main__":
    asyncio.run(main())

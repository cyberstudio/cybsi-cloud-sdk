#!/usr/bin/env python3
import asyncio
from hashlib import md5

from cybsi.cloud import AsyncClient, Config
from cybsi.cloud.iocean.objects import ObjectKeyType, ObjectType


async def main():
    config = Config(api_key="the cryptic string")

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

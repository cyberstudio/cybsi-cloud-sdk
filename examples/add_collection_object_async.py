#!/usr/bin/env python3
import asyncio

from cybsi.cloud import AsyncClient, Config
from cybsi.cloud.iocean.objects import ObjectKeyType, ObjectType


async def main():
    config = Config(api_key="the cryptic string")

    collection_id = "example-collection"
    object_files = (
        (
            ObjectType.File,
            [(ObjectKeyType.MD5Hash, "cea239ce075fcb2151ce9ee10227f042")],
            {"size": 112},
        ),
        (
            ObjectType.File,
            [(ObjectKeyType.MD5Hash, "cea239ce075fcb2151ce9ee10227f032")],
            {"size": 10},
        ),
        (
            ObjectType.File,
            [(ObjectKeyType.MD5Hash, "cea239ce075fcb2151ce9ee10227f022")],
            {"size": 1113},
        ),
        (
            ObjectType.File,
            [(ObjectKeyType.MD5Hash, "cea239ce075fcb2151ce9ee10227f012")],
            {"size": 333},
        ),
    )

    async with AsyncClient(config) as client:
        objects = [
            client.iocean.objects.add(
                collection_id=collection_id,
                obj_type=typ,
                keys=keys,
                context=context,
            )
            for typ, keys, context in object_files
        ]
        await asyncio.gather(*objects)


if __name__ == "__main__":
    asyncio.run(main())

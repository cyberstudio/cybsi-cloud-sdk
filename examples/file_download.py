#!/usr/bin/env python3
import asyncio
import uuid

from cybsi.cloud import AsyncClient, Config


async def main():
    config = Config(api_url="https://cloud.cloud", api_key="the cryptic string")

    async with AsyncClient(config) as client:
        file_id = uuid.UUID("6579dc90-18ab-4b2b-947b-dfa44bd7dcd5")
        with open("/tmp/out.dat", "wb") as f:
            async with await client.filebox.files.download(file_id) as content:
                buf_size = 4096
                buf = await content.read(buf_size)
                while buf:
                    f.write(buf)
                    buf = await content.read(buf_size)


if __name__ == "__main__":
    asyncio.run(main())

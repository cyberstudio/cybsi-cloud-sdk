#!/usr/bin/env python3
import asyncio
from io import BytesIO

from cybsi.cloud import AsyncClient, Config


async def main():
    config = Config(api_url="https://cloud.cloud", api_key="the cryptic string")

    file_data = BytesIO(b"file_data")
    file_name = "example"

    async with AsyncClient(config) as client:
        ref = await client.filebox.files.upload(file_data, name=file_name)
        print(ref.id)


if __name__ == "__main__":
    asyncio.run(main())

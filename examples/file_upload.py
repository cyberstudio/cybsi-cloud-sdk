#!/usr/bin/env python3
import os

from cybsi.cloud import Client, Config

if __name__ == "__main__":
    file_path = "/tmp/file"
    size = os.path.getsize(file_path)

    config = Config(api_key="the cryptic string")
    with Client(config) as client:
        with open(file_path, "rb") as f:
            ref = client.files.upload(f, name=f.name, size=size)
            print(ref.id)

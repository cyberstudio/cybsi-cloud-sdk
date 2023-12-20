#!/usr/bin/env python3
import uuid

from cybsi.cloud import Client, Config

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")
    file_id = uuid.UUID("5d63fd9a-4ffb-46e7-afa1-cfbb0227ad3d")
    buf_size = 4096

    with Client(config) as client:
        with open("/tmp/out.dat", "wb") as f:
            with client.filebox.files.download(file_id) as content:
                buf = content.read(buf_size)
                while buf:
                    f.write(buf)
                    buf = content.read(buf_size)

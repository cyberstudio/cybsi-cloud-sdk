#!/usr/bin/env python3
import os

from cybsi.cloud import Client, Config
from cybsi.cloud.filebox import LimitedReader

if __name__ == "__main__":
    part_size = 10 * (1 << 20)  # 10mb
    file_path = "/tmp/file"
    file_size = os.path.getsize(file_path)

    def iter_part_size():
        rest = file_size
        while rest > 0:
            size = rest if rest < part_size else part_size
            yield size
            rest -= size

    config = Config(api_key="the cryptic string")
    with Client(config) as client:
        session = client.filebox.files.create_session(part_size=part_size)
        with open(file_path, "rb") as f:
            for part_number, part_size in enumerate(iter_part_size(), start=1):
                client.filebox.files.upload_session_part(
                    LimitedReader(f, limit=part_size),
                    session_id=session.id,
                    part_number=part_number,
                    size=part_size,
                )
        ref = client.filebox.files.complete_session(session.id)
        print(ref.id)

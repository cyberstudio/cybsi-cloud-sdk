#!/usr/bin/env python3
import time
from typing import Iterable, Optional

from cybsi.cloud import Client, Config
from cybsi.cloud.iocean import ObjectChangeView
from cybsi.cloud.pagination import Cursor, Page


def main():
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        collection_id = "example-collection"
        _, changes_cursor = client.iocean.objects.filter(
            collection_id=collection_id,
        )

        process_changes(client, collection_id, changes_cursor)


def process_changes(client: Client, collection_id: str, changes_cursor: Cursor):
    fetcher = ChangesFetcher(client, collection_id, changes_cursor)
    while True:
        handle_changes(fetcher.changes())
        # Do not forget to persist last changes cursor
        changes_cursor = fetcher.cursor

        time.sleep(10)


class ChangesFetcher:
    def __init__(self, client: Client, collection_id: str, changes_cursor: Cursor):
        self._client = client
        self._collection_id = collection_id
        self._changes_cursor = changes_cursor

    def changes(self) -> Iterable[ObjectChangeView]:
        """Lazily fetch all available collection changes."""
        page: Optional[Page[ObjectChangeView]] = self._client.iocean.objects.changes(
            collection_id=self._collection_id, cursor=self._changes_cursor
        )

        while page:
            # changes page may return empty cursor.
            # Do not save empty cursor to prevent last cursor lost.
            if page.cursor is not None:
                self._changes_cursor = page.cursor
            yield from page
            page = page.next_page()

    @property
    def cursor(self):
        """Current cursor required to fetch next changes page."""
        return self._changes_cursor


def handle_changes(changes: Iterable[ObjectChangeView]):
    """Handle collection changes."""
    cnt = 0
    for item in changes:
        # Do something with item
        cnt += 1
        pass
    print(f"handled {cnt} changes")


if __name__ == "__main__":
    main()

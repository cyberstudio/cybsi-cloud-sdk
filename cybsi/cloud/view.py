from typing import cast

import httpx

from .api import Tag
from .internal import JsonObjectView


class _TaggedView(JsonObjectView):
    _etag_header = "ETag"

    def __init__(self, resp: httpx.Response):
        super().__init__(resp.json())
        self._tag = cast(Tag, resp.headers.get(self._etag_header, ""))

    @property
    def tag(self) -> Tag:
        """Resource tag.

        Protects against concurrent object changes.
        Alternatively, can be used for caching.
        """
        return self._tag

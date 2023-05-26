"""Use this section of API to access IOCean objects, collections and schemas.
"""
from ..internal import (
    BaseAPI,
)


class IOCeanAPI(BaseAPI):
    """IOCean API."""

    @property
    def collections(self):
        """Get IOCean collections handle."""
        return None  # TODO: implement CollectionsAPI

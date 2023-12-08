from ..internal import BaseAPI, BaseAsyncAPI
from .schemas import SchemaAPI, SchemaAsyncAPI


class InsightAPI(BaseAPI):
    """Insight API."""

    @property
    def schemas(self) -> SchemaAPI:
        """Get Insight schemas handle."""
        return SchemaAPI(self._connector)


class InsightAsyncAPI(BaseAsyncAPI):
    """Insight asynchronous API."""

    @property
    def schemas(self) -> SchemaAsyncAPI:
        """Schemas asynchronous API handle."""
        return SchemaAsyncAPI(self._connector)

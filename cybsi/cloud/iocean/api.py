from ..internal import BaseAPI, BaseAsyncAPI
from .collection import CollectionAPI, CollectionAsyncAPI
from .objects import ObjectAPI, ObjectsAsyncAPI
from .schemas import SchemaAPI, SchemaAsyncAPI


class IOCeanAPI(BaseAPI):
    """IOCean API."""

    @property
    def collections(self) -> CollectionAPI:
        """Get IOCean collections handle."""
        return CollectionAPI(self._connector)

    @property
    def schemas(self) -> SchemaAPI:
        """Get IOCean schemas handle."""
        return SchemaAPI(self._connector)

    @property
    def objects(self) -> ObjectAPI:
        """Objects API handle."""
        return ObjectAPI(self._connector)


class IOCeanAsyncAPI(BaseAsyncAPI):
    """IOCean asynchronous API."""

    @property
    def collections(self) -> CollectionAsyncAPI:
        """Collections asynchronous API handle."""
        return CollectionAsyncAPI(self._connector)

    @property
    def schemas(self) -> SchemaAsyncAPI:
        """Schemas asynchronous API handle."""
        return SchemaAsyncAPI(self._connector)

    @property
    def objects(self) -> ObjectsAsyncAPI:
        """Objects asynchronous API handle."""
        return ObjectsAsyncAPI(self._connector)

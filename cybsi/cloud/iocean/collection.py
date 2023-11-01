from typing import Optional

from ..api import Tag
from ..error import JsonObject
from ..internal import BaseAPI, BaseAsyncAPI, JsonObjectForm, JsonObjectView
from ..pagination import AsyncPage, Cursor, Page
from ..view import _TaggedView
from .schemas import SchemaView

_PATH = "/iocean/collections"


class CollectionAPI(BaseAPI):
    """Collection API"""

    def register(self, collection: "CollectionForm") -> "CollectionRegistrationView":
        """Register collection.

        Note:
            Calls `POST /iocean/collections`.
        Args:
            collection: collection form.
        Return:
            Collection registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.ConflictError`:
                Collection with the specified id (name) already exists.
            :class:`~cybsi.cloud.error.SemanticError`:
                Form contains logic errors.
        Note:
            Conflict error codes specific for this method:
            * :attr:`~cybsi.cloud.error.ConflictErrorCodes.DuplicateCollection`
            Semantic error codes specific for this method:
            * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaNotFound`
        """
        resp = self._connector.do_post(_PATH, json=collection.json())
        return CollectionRegistrationView(resp.json())

    def view(self, collection_id: str) -> "CollectionView":
        """Get collection.

        Note:
            Calls `GET /iocean/collections/{collectionName}`.
        Args:
            collection_id: collection's id.
        Return:
            Collection view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`:
                Resource not found.
        """

        url = f"{_PATH}/{collection_id}"
        resp = self._connector.do_get(url)
        return CollectionView(resp)

    def view_schema(self, collection_id: str) -> SchemaView:
        """Get collection schema.

        Note:
            Calls `GET /iocean/collections/{collectionName}/schema`.
        Args:
            collection_id: collection's id.
        Return:
            Schema view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`:
                Resource not found.
        """

        url = f"{_PATH}/{collection_id}/schema"
        resp = self._connector.do_get(url)
        return SchemaView(resp)

    def update(self, collection_id: str, tag: Tag, *, schema_id: Optional[str]):
        """Update collection

        Note:
            Calls `PATCH /iocean/collections/{collectionName}`.
        Args:
            collection_id: collection's id.
            tag: :attr:`CollectionView.tag` value. Use :meth:`view` to retrieve it.
            schema_id: schema identified.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.ResourceModifiedError`:
                Object schema changed since last request. Update tag and retry.
            :class:`~cybsi.cloud.error.NotFoundError`:
                Resource not found.
            :class:`~cybsi.cloud.error.SemanticError`:
                Form contains logic errors.
        Note:
            Semantic error codes specific for this method:
            * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaNotFound`
        """
        body = {}
        if schema_id is not None:
            body["schemaID"] = schema_id

        url = f"{_PATH}/{collection_id}"
        self._connector.do_patch(url, tag=tag, json=body)

    def filter(
        self,
        *,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> Page["CollectionCommonView"]:
        """Get collections.

        Note:
            Calls `GET /iocean/collections`.
        Args:
            cursor: Page cursor.
            limit: Page limit.
        Return:
            Page with collection views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        resp = self._connector.do_get(path=_PATH, params=params)
        return Page(self._connector.do_get, resp, CollectionCommonView)


class CollectionAsyncAPI(BaseAsyncAPI):
    """Collection asynchronous API"""

    async def register(
        self, collection: "CollectionForm"
    ) -> "CollectionRegistrationView":
        """Register collection.

        Note:
            Calls `POST /iocean/collections`.
        Args:
            collection: collection form.
        Return:
            Collection registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.ConflictError`:
                Collection with the specified id (name) already exists.
            :class:`~cybsi.cloud.error.SemanticError`:
                Form contains logic errors.
        Note:
            Conflict error codes specific for this method:
            * :attr:`~cybsi.cloud.error.ConflictErrorCodes.DuplicateCollection`
            Semantic error codes specific for this method:
            * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaNotFound`
        """
        resp = await self._connector.do_post(_PATH, json=collection.json())
        return CollectionRegistrationView(resp.json())

    async def view(self, collection_id: str) -> "CollectionView":
        """Get collection.

        Note:
            Calls `GET /iocean/collections/{collectionName}`.
        Args:
            collection_id: collection's id.
        Return:
            Collection view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`:
                Resource not found.
        """

        url = f"{_PATH}/{collection_id}"
        resp = await self._connector.do_get(url)
        return CollectionView(resp)

    async def view_schema(self, collection_id: str) -> SchemaView:
        """Get collection schema.

        Note:
            Calls `GET /iocean/collections/{collectionName}/schema`.
        Args:
            collection_id: collection's id.
        Return:
            Schema view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`:
                Resource not found.
        """

        url = f"{_PATH}/{collection_id}/schema"
        resp = await self._connector.do_get(url)
        return SchemaView(resp)

    async def update(self, collection_id: str, tag: Tag, *, schema_id: Optional[str]):
        """Update collection

        Note:
            Calls `PATCH /iocean/collections/{collectionName}`.
        Args:
            collection_id: collection's id.
            tag: :attr:`CollectionView.tag` value. Use :meth:`view` to retrieve it.
            schema_id: schema identified.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.ResourceModifiedError`:
                Object schema changed since last request. Update tag and retry.
            :class:`~cybsi.cloud.error.NotFoundError`:
                Resource not found.
            :class:`~cybsi.cloud.error.SemanticError`:
                Form contains logic errors.
        Note:
            Semantic error codes specific for this method:
            * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaNotFound`
        """
        body = {}
        if schema_id is not None:
            body["schemaID"] = schema_id

        url = f"{_PATH}/{collection_id}"
        await self._connector.do_patch(url, tag=tag, json=body)

    async def filter(
        self,
        *,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> AsyncPage["CollectionCommonView"]:
        """Get collections.

        Note:
            Calls `GET /iocean/collections`.
        Args:
            cursor: Page cursor.
            limit: Page limit.
        Return:
            Page with collection views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        resp = await self._connector.do_get(path=_PATH, params=params)
        return AsyncPage(self._connector.do_get, resp, CollectionCommonView)


class CollectionRegistrationView(JsonObjectView):
    """Collection registration view"""

    @property
    def name(self):
        """The name of registered collection"""
        return self._get("name")


class CollectionCommonView(JsonObjectView):
    """Collection common view"""

    @property
    def name(self) -> str:
        """Collection name"""
        return self._get("name")

    @property
    def schema_id(self) -> str:
        """Schema identifier"""
        return self._get("schemaID")


class CollectionView(_TaggedView, CollectionCommonView):
    """Collection view"""

    pass


class CollectionForm(JsonObjectForm):
    """Collection form"""

    def __init__(self, name: str, schema_id: str):
        super().__init__()
        self._data["name"] = name
        self._data["schemaID"] = schema_id

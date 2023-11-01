from typing import Optional

from ..api import Tag
from ..internal import BaseAPI, BaseAsyncAPI, JsonObject, JsonObjectView
from ..pagination import AsyncPage, Cursor, Page
from ..view import _TaggedView

_PATH = "/iocean/schemas"


class SchemaAPI(BaseAPI):
    """Schema API."""

    def register(self, schema: JsonObject) -> "SchemaRegistrationView":
        """Register an object schema.

        Note:
            Calls `POST /iocean/schemas`.
        Args:
            schema: JSON schema of the object. See :ref:`object_schemas`
                for information about schema structure.
        Returns:
            Schema registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.ConflictError`: Form contains conflict errors.
        Note:
            Conflict error codes specific for this method:
              * :attr:`~cybsi.cloud.error.ConflictErrorCodes.DuplicateSchema`
        """
        resp = self._connector.do_post(path=_PATH, json=schema)
        return SchemaRegistrationView(resp.json())

    def update(
        self,
        *,
        schema_id: str,
        tag: Tag,
        schema: JsonObject,
    ) -> None:
        """Update the object schema.

        Note:
            Calls `PUT /iocean/schemas/{schema_id}`.
        Args:
            schema_id: URL friendly string, uniquely identifies json schema.
            tag: :attr:`SchemaView.tag` value. Use :meth:`view` to retrieve it.
            schema: JSON schema of the object. See :ref:`object_schemas`
                for information about schema structure.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
            :class:`~cybsi.cloud.error.ResourceModifiedError`:
                Object schema changed since last request. Update tag and retry.
            :class:`~cybsi.cloud.error.NotFoundError`: Object schema not found.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidSchemaID`
        """

        path = f"{_PATH}/{schema_id}"
        self._connector.do_put(path=path, tag=tag, json=schema)

    def view(self, schema_id: str) -> "SchemaView":
        """Get the object schema view.

        Note:
            Calls `GET /iocean/schemas/{schema_id}`.
        Args:
            schema_id: URL friendly string, uniquely identifies json schema.
        Returns:
            Schema view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Object schema not found.
        """

        path = f"{_PATH}/{schema_id}"
        resp = self._connector.do_get(path=path)
        return SchemaView(resp)

    def filter(
        self,
        *,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> Page["SchemaCommonView"]:
        """Get an object schemas filtration list.

        Note:
            Calls `GET /iocean/schemas`.
        Args:
            cursor: Page cursor.
            limit: Page limit.
        Returns:
             Page with schema common views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
        """

        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        resp = self._connector.do_get(path=_PATH, params=params)
        return Page(self._connector.do_get, resp, SchemaCommonView)


class SchemaAsyncAPI(BaseAsyncAPI):
    """Schema asynchronous API."""

    async def register(self, schema: JsonObject) -> "SchemaRegistrationView":
        """Register an object schema.

        Note:
            Calls `POST /iocean/schemas`.
        Args:
            schema: JSON schema of the object. See :ref:`object_schemas`
                for information about schema structure.
        Returns:
            Schema registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.ConflictError`: Form contains conflict errors.
        Note:
            Conflict error codes specific for this method:
              * :attr:`~cybsi.cloud.error.ConflictErrorCodes.DuplicateSchema`
        """
        resp = await self._connector.do_post(path=_PATH, json=schema)
        return SchemaRegistrationView(resp.json())

    async def update(
        self,
        *,
        schema_id: str,
        tag: Tag,
        schema: JsonObject,
    ) -> None:
        """Update the object schema.

        Note:
            Calls `PUT /iocean/schemas/{schema_id}`.
        Args:
            schema_id: URL friendly string, uniquely identifies json schema.
            tag: :attr:`SchemaView.tag` value. Use :meth:`view` to retrieve it.
            schema: JSON schema of the object. See :ref:`object_schemas`
                for information about schema structure.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
            :class:`~cybsi.cloud.error.ResourceModifiedError`:
                Object schema changed since last request. Update tag and retry.
            :class:`~cybsi.cloud.error.NotFoundError`: Object schema not found.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidSchemaID`
        """

        path = f"{_PATH}/{schema_id}"
        await self._connector.do_put(path=path, tag=tag, json=schema)

    async def view(self, schema_id: str) -> "SchemaView":
        """Get the object schema view.

        Note:
            Calls `GET /iocean/schemas/{schema_id}`.
        Args:
            schema_id: URL friendly string, uniquely identifies json schema.
        Returns:
            Schema view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Object schema not found.
        """

        path = f"{_PATH}/{schema_id}"
        resp = await self._connector.do_get(path=path)
        return SchemaView(resp)

    async def filter(
        self,
        *,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> AsyncPage["SchemaCommonView"]:
        """Get an object schemas filtration list.

        Note:
            Calls `GET /iocean/schemas`.
        Args:
            cursor: Page cursor.
            limit: Page limit.
        Returns:
             Page with schema common views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
        """

        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        resp = await self._connector.do_get(path=_PATH, params=params)
        return AsyncPage(self._connector.do_get, resp, SchemaCommonView)


class SchemaRegistrationView(JsonObjectView):
    """Schema registration view"""

    @property
    def schema_id(self) -> str:
        """URL friendly string, uniquely identifies json schema."""
        return self._get("schemaID")


class SchemaCommonView(JsonObjectView):
    """Schema common view"""

    @property
    def schema_id(self) -> str:
        """URL friendly string, uniquely identifies json schema."""
        return self._get("schemaID")

    @property
    def title(self) -> str:
        """The human-readable name of the json schema."""
        return self._get("title")


class SchemaView(_TaggedView):
    """Schema view"""

    @property
    def schema_id(self) -> str:
        """URL friendly string, uniquely identifies json schema."""
        return self._get("schemaID")

    @property
    def schema(self) -> JsonObject:
        """JSON schema of the object

        See :ref:`object_schemas` for information about schema structure.
        """
        return self.raw()

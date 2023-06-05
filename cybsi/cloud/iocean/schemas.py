from typing import Optional

from ..api import Tag
from ..internal import BaseAPI, JsonObject, JsonObjectView
from ..pagination import Cursor, Page
from ..view import _TaggedView


class SchemasAPI(BaseAPI):
    """Schemas API."""

    _path = "/schemas"

    def register(self, schema: JsonObject) -> "SchemaRegistrationView":
        """Register an object schema.

        Note:
            Calls `POST /schemas`.
        Args:
            schema: JSON schema of the object. See :ref:`object_schemas`
                for information about schema structure.
        Returns:
            Schema registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
            :class:`~cybsi.cloud.error.ConflictError`: Form contains conflict errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidSchema`
            Conflict error codes specific for this method:
              * :attr:`~cybsi.cloud.error.ConflictErrorCodes.DuplicateSchema`
        """
        resp = self._connector.do_post(path=self._path, json=schema)
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
            Calls `PUT /schemas/{schema_id}`.
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
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidSchema`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidSchemaID`
        """

        path = f"{self._path}/{schema_id}"
        self._connector.do_put(path=path, tag=tag, json=schema)

    def view(self, schema_id: str) -> "SchemaView":
        """Get the object schema view.

        Note:
            Calls `GET /schemas/{schema_id}`.
        Args:
            schema_id: URL friendly string, uniquely identifies json schema.
        Returns:
            Schema view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Object schema not found.
        """

        path = f"{self._path}/{schema_id}"
        resp = self._connector.do_get(path=path)
        return SchemaView(resp)

    def filter(
        self,
        *,
        cursor: Optional[Cursor] = None,
    ) -> Page["SchemaCommonView"]:
        """Get an object schemas filtration list.

        Note:
            Calls `GET /schemas`.
        Args:
            cursor: Page cursor.
        Returns:
             Page with schema common views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
        """

        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        resp = self._connector.do_get(path=self._path, params=params)
        page = Page(self._connector.do_get, resp, SchemaCommonView)
        return page


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
        return self._data

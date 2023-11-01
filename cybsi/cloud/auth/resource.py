from typing import Optional

from ..error import JsonObject
from ..internal import BaseAPI, JsonObjectView
from ..pagination import Cursor, Page


class ResourcesAPI(BaseAPI):
    """Resources API."""

    _path = "/auth/resources"

    def filter(
        self,
        *,
        parent_id: Optional[int] = None,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> Page["ResourceView"]:
        """Get resources.

        Note:
            Calls `GET /auth/resources`.
        Args:
            parent_id: identifier of parent resource. It must be greater than 0.
            cursor: Page cursor.
            limit: Page limit.
        Return:
            Page with resource common views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
        Note:
            Semantic error codes specific for this method:
            * :attr:`~cybsi.cloud.error.SemanticErrorCodes.ResourceNotFound`
        """
        params: JsonObject = {}
        if parent_id is not None:
            params["parentID"] = parent_id
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        resp = self._connector.do_get(path=self._path, params=params)
        page = Page(self._connector.do_get, resp, ResourceView)
        return page


class ResourceRefView(JsonObjectView):
    """Resource reference view."""

    @property
    def id(self) -> int:
        """API-Key identifier."""
        return self._get("id")


class ResourceView(JsonObjectView):
    """Resource view."""

    @property
    def id(self) -> int:
        """Resource identifier."""
        return self._get("id")

    @property
    def name(self) -> str:
        """Resource name."""
        return self._get("name")

    @property
    def parent(self) -> Optional[ResourceRefView]:
        """Parent resource."""
        return self._map_optional("parent", ResourceRefView)

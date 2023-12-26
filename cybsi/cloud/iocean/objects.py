from typing import Iterable, List, Optional, Tuple, cast
from urllib.parse import parse_qs, urlparse

import httpx
from enum_tools import document_enum

from ..enum import CybsiAPIEnum
from ..internal import BaseAPI, BaseAsyncAPI, JsonObject, JsonObjectView
from ..pagination import AsyncPage, Cursor, Page

_PATH = "/iocean/collections/{}/objects"


@document_enum
class ObjectKeyType(CybsiAPIEnum):
    """Object key type."""

    MD5Hash = "MD5Hash"
    SHA1Hash = "SHA1Hash"
    SHA256Hash = "SHA256Hash"
    SHA512Hash = "SHA512Hash"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"
    IPNetwork = "IPNetwork"


@document_enum
class ObjectType(CybsiAPIEnum):
    """Object type."""

    File = "File"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"
    IPNetwork = "IPNetwork"


@document_enum
class ObjectOperation(CybsiAPIEnum):
    """Object change operation."""

    Add = "Add"
    """Object was added to collection."""
    Remove = "Remove"
    """Object war removed from collection."""
    Update = "Update"
    """Object in collection was updated."""


class ObjectAPI(BaseAPI):
    """Object API."""

    def add(
        self,
        *,
        collection_id: str,
        obj_type: ObjectType,
        keys: Iterable[Tuple[ObjectKeyType, str]],
        context: JsonObject = {},
    ) -> None:
        """Add object to collection.

        If there is registered object with corresponding keys
        and there are no keys conflicts, this method:
        - rewrites object context with new one;
        - extends key set of the registered object.

        Note:
            Calls `POST /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            obj_type: Type of the object.
            keys: Keys of the object.
            context: Additional data describing object.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.KeySetConflict`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaCheckFail`
        """
        path = _PATH.format(collection_id)
        payload = {
            "type": obj_type.value,
            "keys": [{"type": key[0].value, "value": key[1]} for key in keys],
            "context": context,
        }
        self._connector.do_post(path=path, json=payload)

    def delete(
        self,
        *,
        collection_id: str,
        key_type: ObjectKeyType,
        key_value: str,
    ) -> None:
        """Delete object from collection.

        Note:
            Calls `DELETE /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            key_type: Key type of object to be removed.
            key_value: Key value of object to be removed.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
        """
        params: JsonObject = {
            "objectKeyType": key_type.value,
            "objectKey": key_value,
        }
        path = _PATH.format(collection_id)
        self._connector.do_delete(path=path, params=params)

    def filter(
        self,
        *,
        collection_id: str,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Page["ObjectView"], Optional[Cursor]]:
        """Get objects from the collection.

        Note:
            Calls `GET /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            cursor: Page cursor.
            limit: Page limit.
        Return:
            Page with object views. The page contains next page cursor.
            Changes cursor. The cursor can be used to call :meth:`changes`.
        Note:
            Changes cursor is returned only on the first page.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        path = _PATH.format(collection_id)
        resp = self._connector.do_get(path=path, params=params)
        return Page(self._connector.do_get, resp, ObjectView), _extract_changes_cursor(
            resp
        )

    def changes(
        self,
        *,
        collection_id: str,
        cursor: Cursor,
        limit: Optional[int] = None,
    ) -> Page["ObjectChangeView"]:
        """Get objects changes from the collection.

        Note:
            Calls `GET /iocean/collections/{collection_id}/objects/changes`.
        Args:
            collection_id: Collection identifier.
            cursor: Page cursor.
                On the first request you should pass the cursor value
                obtained when requesting objects :meth:`filter`.
                Subsequent calls should use cursor property of the page
                returned by :meth:`changes`.
            limit: Page limit.
        Return:
            Page with changes.
        Warning:
            Cursor behaviour differs from other API methods.

            Do not save returned page cursor if it is :data:`None`.
            :data:`None` means that all changes **for this moment** are received.
            More changes can arrive later. Pass your previous non-none ``cursor``
            value in loop, until :data:`None` cursor is returned.

            Please wait some time if method returns a page with :data:`None` cursor.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Semantic request error.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.CursorOutOfRange`
        """
        params: JsonObject = {"cursor": cursor}
        if limit is not None:
            params["limit"] = limit
        path = _PATH.format(collection_id) + "/changes"
        resp = self._connector.do_get(path=path, params=params)
        return Page(self._connector.do_get, resp, ObjectChangeView)


class ObjectsAsyncAPI(BaseAsyncAPI):
    """Object asynchronous API."""

    async def add(
        self,
        *,
        collection_id: str,
        obj_type: ObjectType,
        keys: Iterable[Tuple[ObjectKeyType, str]],
        context: JsonObject = {},
    ) -> None:
        """Add object to collection.

        If there is registered object with corresponding keys
        and there are no keys conflicts, this method:
        - rewrites object context with new one;
        - extends key set of the registered object.

        Note:
            Calls `POST /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            obj_type: Type of the object.
            keys: Keys of the object.
            context: Additional data describing object.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.KeySetConflict`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaCheckFail`
        """
        path = _PATH.format(collection_id)
        payload = {
            "type": obj_type.value,
            "keys": [{"type": key[0].value, "value": key[1]} for key in keys],
            "context": context,
        }
        await self._connector.do_post(path=path, json=payload)

    async def delete(
        self,
        *,
        collection_id: str,
        key_type: ObjectKeyType,
        key_value: str,
    ) -> None:
        """Delete object from collection.

        Note:
            Calls `DELETE /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            key_type: Key type of object to be removed.
            key_value: Key value of object to be removed.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
        """
        params: JsonObject = {
            "objectKeyType": key_type.value,
            "objectKey": key_value,
        }
        path = _PATH.format(collection_id)
        await self._connector.do_delete(path=path, params=params)

    async def filter(
        self,
        *,
        collection_id: str,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> Tuple[AsyncPage["ObjectView"], Optional[Cursor]]:
        """Get objects from the collection.

        Note:
            Calls `GET /iocean/collections/{collection_id}/objects`.
        Args:
            collection_id: Collection identifier.
            cursor: Page cursor.
            limit: Page limit.
        Return:
            Page with object views. The page contains next page cursor.
            Changes cursor. The cursor can be used to call :meth:`changes`.
        Note:
            Changes cursor is returned only on the first page.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        path = _PATH.format(collection_id)
        resp = await self._connector.do_get(path=path, params=params)
        return AsyncPage(
            self._connector.do_get, resp, ObjectView
        ), _extract_changes_cursor(resp)

    async def changes(
        self,
        *,
        collection_id: str,
        cursor: Cursor,
        limit: Optional[int] = None,
    ) -> AsyncPage["ObjectChangeView"]:
        """Get objects changes from the collection.

        Note:
            Calls `GET /iocean/collections/{collection_id}/objects/changes`.
        Args:
            collection_id: Collection identifier.
            cursor: Page cursor.
                On the first request you should pass the cursor value
                obtained when requesting objects :meth:`filter`.
                Subsequent calls should use cursor property of the page
                returned by :meth:`changes`.
            limit: Page limit.
        Return:
            Page with changes.
        Warning:
            Cursor behaviour differs from other API methods.

            Do not save returned page cursor if it is :data:`None`.
            :data:`None` means that all changes **for this moment** are received.
            More changes can arrive later. Pass your previous non-none ``cursor``
            value in loop, until :data:`None` cursor is returned.

            Please wait some time if method returns a page with :data:`None` cursor.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Collection not found.
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Semantic request error.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.CursorOutOfRange`
        """
        params: JsonObject = {"cursor": cursor}
        if limit is not None:
            params["limit"] = limit
        path = _PATH.format(collection_id) + "/changes"
        resp = await self._connector.do_get(path=path, params=params)
        return AsyncPage(self._connector.do_get, resp, ObjectChangeView)


def _extract_changes_cursor(resp: httpx.Response) -> Optional[Cursor]:
    """Extracts changes cursor from response."""
    related_url = resp.links.get("related", {}).get("url")
    if related_url is None:
        return None
    parsed = urlparse(related_url)
    query = parse_qs(parsed.query)
    cursor = query["cursor"]
    return cast(Optional[Cursor], cursor[0]) if cursor is not None else None


class ObjectKeyView(JsonObjectView):
    """Object key view"""

    @property
    def type(self) -> ObjectKeyType:
        """Object key type"""
        return ObjectKeyType.from_string(self._get("type"))

    @property
    def value(self) -> str:
        """Key value."""
        return self._get("value")


class ObjectView(JsonObjectView):
    """Object view."""

    @property
    def type(self) -> ObjectType:
        """Object type."""
        return ObjectType.from_string(self._get("type"))

    @property
    def keys(self) -> List[ObjectKeyView]:
        """Object keys."""
        return [ObjectKeyView(key) for key in self._get("keys")]

    @property
    def context(self) -> JsonObject:
        """Object context."""
        return cast(JsonObject, self._get("context"))


class ObjectChangeView(JsonObjectView):
    """Object change view."""

    @property
    def operation(self) -> ObjectOperation:
        """Object operation."""
        return ObjectOperation.from_string(self._get("operation"))

    @property
    def obj(self) -> ObjectView:
        """Object."""
        return ObjectView(self._get("object"))

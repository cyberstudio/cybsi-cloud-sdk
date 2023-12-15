import asyncio
import json
import logging
import threading
from datetime import datetime
from typing import AsyncGenerator, Generator, Iterable, List, Optional
from urllib.parse import urljoin

import httpx

from ..error import _raise_cybsi_error
from ..internal import (
    BaseAPI,
    JsonObject,
    JsonObjectForm,
    JsonObjectView,
    parse_rfc3339_timestamp,
    rfc3339_timestamp,
)
from ..pagination import Cursor, Page
from .limits import RequestLimitForm, RequestLimitView
from .permission import ResourcePermissionForm, ResourcePermissionView
from .token import TokenView

logger = logging.getLogger(__name__)


class APIKeyAuth(httpx.Auth):
    """Automatically handles authentication
    of :class:`~cybsi.cloud.Client` requests using API key.

    Args:
        api_url: Cybsi Cloud auth API URL. Usually equal to Client config API URL.
        api_key: Cybsi Cloud API key.
    """

    requires_response_body = True  # instructs httpx to pass token request response body

    _get_token_path = "/auth/token"

    def __init__(self, *, api_url: str, api_key: str):
        # See https://www.python-httpx.org/advanced/#customizing-authentication
        self._api_key = api_key
        self._api_url = api_url
        self._sync_lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        self._token = ""

    def sync_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        token = self._token
        if token:
            request.headers["Authorization"] = self._token
            response = yield request
            if response.status_code != 401:
                return

        with self._sync_lock:
            if self._token == token:
                token_response = yield self._build_token_request(request)
                self._update_token(token_response, token_response.read())
            request.headers["Authorization"] = self._token
            yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        token = self._token
        if token:
            request.headers["Authorization"] = self._token
            response = yield request
            if response.status_code != 401:
                return

        async with self._async_lock:
            if self._token == token:
                token_response = yield self._build_token_request(request)
                self._update_token(token_response, await token_response.aread())
            request.headers["Authorization"] = self._token
            yield request

    def _build_token_request(self, req) -> httpx.Request:
        token_url = urljoin(self._api_url, self._get_token_path)
        headers = {
            "X-Api-Version": req.headers["X-Api-Version"],
            "User-Agent": req.headers["User-Agent"],
            "X-Api-Key": self._api_key,
        }
        return httpx.Request(
            "GET",
            url=token_url,
            headers=headers,
        )

    def _update_token(
        self, token_response: httpx.Response, token_response_content: bytes
    ) -> None:
        if not token_response.is_success:
            _raise_cybsi_error(token_response)
        token = TokenView(json.loads(token_response_content))

        self._token = f"{token.type.value} {token.access_token}"


class APIKeysAPI(BaseAPI):
    """API-Keys API."""

    _path = "/auth/keys"

    def filter(
        self,
        *,
        revoked: Optional[bool] = None,
        description: Optional[str] = None,
        cursor: Optional[Cursor] = None,
        limit: Optional[int] = None,
    ) -> Page["APIKeyView"]:
        """Get API keys.

        Note:
            Calls `GET /auth/keys`.
        Args:
            revoked: Revocation flag.
            description: Key description.
            cursor: Page cursor.
            limit: Page limit.
        Return:
            Page with API-Key common views and next page cursor.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        params: JsonObject = {}
        if cursor is not None:
            params["cursor"] = str(cursor)
        if limit is not None:
            params["limit"] = limit
        if revoked is not None:
            params["revoked"] = bool(revoked)
        if description is not None:
            params["description"] = str(description)
        resp = self._connector.do_get(path=self._path, params=params)
        page = Page(self._connector.do_get, resp, APIKeyView)
        return page

    def generate(self, api_key: "APIKeyForm") -> "APIKeyRegistrationView":
        """Generate new API-Key.

        Note:
            Calls `POST /auth/keys`.
        Args:
            api_key: API-Key.
        Returns:
            API-Key view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.ResourceNotFound`
        """

        resp = self._connector.do_post(path=self._path, json=api_key.json())
        return APIKeyRegistrationView(resp.json())

    def revoke(
        self,
        api_key_id: int,
    ):
        """Revoke API-Key.

        Warning:
            Key revocation is an irreversible operation.
        Note:
            Calls `POST /auth/keys/{api_key_id}/revoked`.
        Args:
            api_key_id: API-Key identifier.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: Resource not found.
        """

        path = f"{self._path}/{api_key_id}/revoked"
        self._connector.do_post(path=path)


class APIKeyForm(JsonObjectForm):
    """API-Key form.

    This is the form you need to fill to generate API-Key.

    Args:
        permissions: List of permissions.
        expires_at: Expiration date.
            The API-Key is automatically disabled after the expiration date.
        description: API-Key description.
        request_limits: List of API-Key request limits.
    """

    def __init__(
        self,
        permissions: Iterable[ResourcePermissionForm],
        *,
        request_limits: Optional[Iterable[RequestLimitForm]] = None,
        expires_at: Optional[datetime] = None,
        description: Optional[str] = None,
    ):
        super().__init__()
        if expires_at is not None:
            self._data["expiresAt"] = rfc3339_timestamp(expires_at)
        if description is not None:
            self._data["description"] = description
        if request_limits is not None:
            self._data["requestLimits"] = [limit.json() for limit in request_limits]
        self._data["permissions"] = [perm.json() for perm in permissions]


class APIKeyRegistrationView(JsonObjectView):
    """API-Key view."""

    @property
    def id(self) -> int:
        """API-Key identifier."""
        return self._get("id")

    @property
    def key(self) -> str:
        """API-Key value.

        Warning:
            Do not forget to save this value. It is not recoverable if lost."""
        return self._get("key")


class APIKeyView(JsonObjectView):
    """API-Key view."""

    @property
    def id(self) -> int:
        """API-Key identifier."""
        return self._get("id")

    @property
    def created_at(self) -> datetime:
        """Creation date."""
        return parse_rfc3339_timestamp(self._get("createdAt"))

    @property
    def expires_at(self) -> Optional[datetime]:
        """Expiration date.
        The API-Key is automatically disabled after the expiration date."""
        return self._map_optional("expiresAt", parse_rfc3339_timestamp)

    @property
    def description(self) -> Optional[str]:
        """API-Key description."""
        return self._get_optional("description")

    @property
    def last_used_at(self) -> Optional[datetime]:
        """Last usage date."""
        return self._map_optional("lastUsedAt", parse_rfc3339_timestamp)

    @property
    def revoked(self) -> bool:
        """API-Key revoked flag."""
        return self._get("revoked")

    @property
    def permissions(self) -> List[ResourcePermissionView]:
        """List of permissions."""
        return [ResourcePermissionView(perm) for perm in self._get("permissions")]

    @property
    def request_limits(self) -> List[RequestLimitView]:
        """List of request limits."""
        return [RequestLimitView(limit) for limit in self._get("requestLimits")]

import asyncio
import json
import logging
import threading
from typing import AsyncGenerator, Generator
from urllib.parse import urljoin

import httpx

from ..error import _raise_cybsi_error
from ..internal import BaseAPI
from .token import TokenView

logger = logging.getLogger(__name__)


class APIKeyAuth(httpx.Auth):
    """Authomatically handles authentication
    of :class:`~cybsi.cloud.Client` requests using API key.

    Args:
        api_url: Cybsi Cloud auth API URL. Usually equal to Client config API URL.
        api_key: Cybsi Cloud API key.
    Usage:
        >>> TODO: add example
    """

    requires_response_body = True  # instructs httpx to pass token request response body

    _get_token_path = "auth/token"

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

        with self._sync_lock:
            if self._token:
                request.headers["Authorization"] = self._token
                response = yield request

            if not self._token or response.status_code == 401:
                token_response = yield self._build_token_request(request)
                self._update_token(token_response, token_response.read())

                request.headers["Authorization"] = self._token
                yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        async with self._async_lock:
            if self._token:
                request.headers["Authorization"] = self._token
                response = yield request

            if not self._token or response.status_code == 401:
                token_response = yield self._build_token_request(request)
                self._update_token(token_response, await token_response.aread())

                request.headers["Authorization"] = self._token
                yield request

    def _build_token_request(self, req) -> httpx.Request:
        token_url = urljoin(self._api_url, self._get_token_path)
        headers = {"User-Agent": req.headers["User-Agent"], "X-Api-Key": self._api_key}
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

    pass

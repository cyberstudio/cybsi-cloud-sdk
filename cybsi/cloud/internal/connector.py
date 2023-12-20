from typing import Any, Optional

import httpx

from cybsi.__version__ import __version__

from ..api import Tag
from ..error import CybsiError, _raise_cybsi_error
from ..internal.multipart import apply_async_multipart_stream

_BASIC_HEADERS = {
    "User-Agent": f"cybsi-cloud-client/v{__version__}",
    "X-Api-Version": "1",
}

_IF_MATCH_HEADER = "If-Match"

apply_async_multipart_stream()


class HTTPConnector:
    """Connector performing round trips to Cybsi Cloud."""

    def __init__(
        self,
        base_url: str,
        auth: Any,
        ssl_verify: bool,
        timeouts,
        limits,
    ):
        self._client = httpx.Client(
            auth=auth,
            verify=ssl_verify,
            base_url=base_url,
            headers=_BASIC_HEADERS,
            timeout=timeouts._as_httpx_timeouts(),
            limits=limits._as_httpx_limits(),
        )

    def __enter__(self) -> "HTTPConnector":
        self._client.__enter__()
        return self

    def __exit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        self._client.__exit__(exc_type, exc_value, traceback)

    def close(self) -> None:
        """Close client and release connections."""
        self._client.close()

    def do_get(
        self, path: str, params: Optional[dict] = None, stream=False, **kwargs
    ) -> httpx.Response:
        if params is None:
            params = {}
        return self._do("GET", path, params=params, stream=stream, **kwargs)

    def do_post(self, path: str, json: Any = None, **kwargs) -> httpx.Response:
        return self._do("POST", path, json=json, **kwargs)

    def do_patch(
        self, path: str, tag: Tag, json: Any = None, **kwargs
    ) -> httpx.Response:
        headers = kwargs.setdefault("headers", {})
        headers[_IF_MATCH_HEADER] = tag
        return self._do("PATCH", path, json=json, **kwargs)

    def do_put(
        self, path: str, tag: Optional[Tag] = None, json: Any = None, **kwargs
    ) -> httpx.Response:
        if tag is not None:
            headers = kwargs.setdefault("headers", {})
            headers[_IF_MATCH_HEADER] = tag
        return self._do("PUT", path, json=json, **kwargs)

    def do_delete(
        self, path: str, params: Optional[dict] = None, **kwargs
    ) -> httpx.Response:
        return self._do("DELETE", path, params=params, **kwargs)

    def do_head(self, path: str, **kwargs) -> httpx.Response:
        return self._do("HEAD", path, **kwargs)

    def _do(self, method: str, path: str, stream=False, **kwargs):
        """Do HTTP request.

        Args:
            method: HTTP method i.e GET, POST, PUT.
            path: URL path.
            kwargs: Any kwargs supported by httpx.Request.
        Return:
            Response.
        Raise:
            :class:`~cybsi.cloud.error.CybsiError`: On connectivity issues.
            :class:`~cybsi.cloud.error.APIError`: If response status code is >= 400
        """
        req = self._client.build_request(method, url=path, **kwargs)
        try:
            resp = self._client.send(request=req, stream=stream)
        except CybsiError:
            raise
        except httpx.TimeoutException as exp:
            # Handle httpx.TimeoutException separately
            # because it doesn't have an exception message.
            raise CybsiError("request timeout", exp) from exp
        except Exception as exp:
            raise CybsiError("could not send request", exp) from exp

        if not resp.is_success:
            if resp.stream:  # type: ignore
                # read stream data to raise the error
                resp.read()
            _raise_cybsi_error(resp)

        return resp


class AsyncHTTPConnector:
    """Asynchronous connector performing round trips to Cybsi Cloud."""

    def __init__(
        self,
        base_url: str,
        auth: Any,
        ssl_verify: bool,
        timeouts,
        limits,
    ):
        self._client = httpx.AsyncClient(
            auth=auth,
            verify=ssl_verify,
            base_url=base_url,
            headers=_BASIC_HEADERS,
            timeout=timeouts._as_httpx_timeouts(),
            limits=limits._as_httpx_limits(),
        )

    async def __aenter__(self) -> "AsyncHTTPConnector":
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc_value, traceback)

    async def aclose(self) -> None:
        """Close client and release connections."""
        await self._client.aclose()

    async def do_get(
        self, path: str, params: Optional[dict] = None, stream=False, **kwargs
    ) -> httpx.Response:
        if params is None:
            params = {}
        return await self._do("GET", path, params=params, stream=stream, **kwargs)

    async def do_post(self, path: str, json=None, **kwargs) -> httpx.Response:
        return await self._do("POST", path, json=json, **kwargs)

    async def do_patch(
        self, path: str, tag: Tag, json: Any = None, **kwargs
    ) -> httpx.Response:
        headers = kwargs.setdefault("headers", {})
        headers[_IF_MATCH_HEADER] = tag
        return await self._do("PATCH", path, json=json, **kwargs)

    async def do_put(
        self, path: str, tag: Optional[Tag] = None, json=None, **kwargs
    ) -> httpx.Response:
        if tag is not None:
            headers = kwargs.setdefault("headers", {})
            headers[_IF_MATCH_HEADER] = tag
        return await self._do("PUT", path, json=json, **kwargs)

    async def do_delete(
        self, path: str, params: Optional[dict] = None, **kwargs
    ) -> httpx.Response:
        return await self._do("DELETE", path, params=params, **kwargs)

    async def do_head(self, path: str, **kwargs) -> httpx.Response:
        return await self._do("HEAD", path, **kwargs)

    async def _do(self, method: str, path: str, stream=False, **kwargs):
        """Do HTTP request.

        Args:
            method: HTTP method i.e GET, POST, PUT.
            path: URL path.
            kwargs: Any kwargs supported by httpx.Request.
        Return:
            Response.
        Raise:
            :class:`~cybsi.cloud.error.CybsiError`: On connectivity issues.
            :class:`~cybsi.cloud.error.APIError`: If response status code is >= 400
        """
        req = self._client.build_request(method, url=path, **kwargs)
        try:
            resp = await self._client.send(request=req, stream=stream)
        except CybsiError:
            raise
        except httpx.TimeoutException as exp:
            # Handle httpx.TimeoutException separately
            # because it doesn't have an exception message.
            raise CybsiError("request timeout", exp) from exp
        except Exception as exp:
            raise CybsiError("could not send request", exp) from exp

        if not resp.is_success:
            if resp.stream:  # type: ignore
                # read stream data to raise the error
                await resp.aread()
            _raise_cybsi_error(resp)

        return resp

import asyncio
from typing import Callable, Optional
from unittest.mock import patch

import httpx
import pytest

from cybsi.cloud.auth import APIKeyAuth
from cybsi.cloud.client_config import _DEFAULT_LIMITS, _DEFAULT_TIMEOUTS
from cybsi.cloud.error import (
    APIError,
    ForbiddenError,
    ForbiddenErrorCodes,
    TooManyRequestsError,
    TooManyRequestsErrorCodes,
    UnauthorizedError,
    _raise_cybsi_error,
)
from cybsi.cloud.internal import AsyncHTTPConnector, HTTPConnector
from cybsi.cloud.pagination import AsyncPage, Page

BASE_URL = "https://api.example.test"
ERROR_CASES = [
    (401, UnauthorizedError, "Unauthorized"),
    (403, ForbiddenError, "Forbidden"),
    (429, TooManyRequestsError, "LimitExceeded"),
]
INVALID_BODIES = [
    b"",
    b"Access denied",
    b"<html>Access denied</html>",
    b'{"code":',
    b"null",
    b"[]",
    b'[["code", "Unexpected"]]',
    b'"Access denied"',
    b"42",
    b"true",
]


@pytest.mark.parametrize("status,error_type,code", ERROR_CASES)
@pytest.mark.parametrize("body", INVALID_BODIES)
def test_non_object_error_body_preserves_http_error(status, error_type, code, body):
    response = httpx.Response(status, content=body)

    with pytest.raises(error_type) as raised:
        _raise_cybsi_error(response)

    error = raised.value
    assert isinstance(error, APIError)
    assert error._status == status
    assert error.content.code == code
    assert error.content.message == (response.text or "Empty response body")
    assert error.content.message in str(error)
    if status == 403:
        assert error.code is ForbiddenErrorCodes.Forbidden
    elif status == 429:
        assert error.code is TooManyRequestsErrorCodes.LimitExceeded


@pytest.mark.parametrize(
    "status,error_type,code",
    [
        (401, UnauthorizedError, "Unauthorized"),
        (403, ForbiddenError, "MissingPermissions"),
        (429, TooManyRequestsError, "LimitExceeded"),
    ],
)
def test_valid_error_object_is_preserved(status, error_type, code):
    content = {
        "code": code,
        "message": "Operation rejected",
        "details": {"permission": "Objects:r"},
        "extra": "preserved",
    }

    error = error_type(httpx.Response(status, json=content))

    assert error._status == status
    assert error.content == content
    assert error.content.details == content["details"]
    if status != 401:
        assert error.code.value == code


@pytest.mark.parametrize("content", [{}, {"message": "No error code"}])
@pytest.mark.parametrize("status,error_type,code", ERROR_CASES)
def test_json_objects_are_not_replaced(status, error_type, code, content):
    error = error_type(httpx.Response(status, json=content))

    assert error.content == content


@pytest.mark.parametrize("retry_after,expected", [(None, None), ("0", 0), ("120", 120)])
@pytest.mark.parametrize("valid_json", [False, True])
def test_retry_after_is_preserved(retry_after, expected, valid_json):
    headers = {} if retry_after is None else {"Retry-After": retry_after}
    response = (
        httpx.Response(
            429,
            headers=headers,
            json={"code": "LimitExceeded", "message": "Try later"},
        )
        if valid_json
        else httpx.Response(429, headers=headers, content=b"Try later")
    )

    error = TooManyRequestsError(response)

    assert error.retry_after == expected


def _request(
    handler: Callable,
    asynchronous: bool,
    *,
    auth_factory: Optional[Callable] = None,
    stream: bool = False,
    paginate: bool = False,
):
    client_type = httpx.AsyncClient if asynchronous else httpx.Client

    def make_client(**kwargs):
        return client_type(transport=httpx.MockTransport(handler), **kwargs)

    def make_connector(connector_type):
        return connector_type(
            base_url=BASE_URL,
            auth=auth_factory() if auth_factory is not None else None,
            ssl_verify=True,
            timeouts=_DEFAULT_TIMEOUTS,
            limits=_DEFAULT_LIMITS,
            retry=0,
        )

    async def request_async():
        async with make_connector(AsyncHTTPConnector) as connector:
            response = await connector.do_get("/objects", stream=stream)
            if paginate:
                return await AsyncPage(connector.do_get, response, dict).next_page()
            return response

    with patch(
        "cybsi.cloud.internal.connector.httpx." + client_type.__name__,
        side_effect=make_client,
    ):
        if asynchronous:
            return asyncio.run(request_async())
        # Python 3.8/3.9 auth locks need a current loop even for sync requests.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with make_connector(HTTPConnector) as connector:
                response = connector.do_get("/objects", stream=stream)
                if paginate:
                    return Page(connector.do_get, response, dict).next_page()
                return response
        finally:
            asyncio.set_event_loop(None)
            loop.close()


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("stream", [False, True], ids=["buffered", "streamed"])
@pytest.mark.parametrize("status,error_type,code", ERROR_CASES)
def test_connector_preserves_non_json_http_error(
    asynchronous, stream, status, error_type, code
):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status, stream=httpx.ByteStream(b"<html>Access denied</html>")
        )

    with pytest.raises(error_type) as raised:
        _request(handler, asynchronous, stream=stream)

    assert raised.value._status == status
    assert raised.value.content.code == code
    assert raised.value.content.message == "<html>Access denied</html>"
    assert len(requests) == 1


def _auth():
    return APIKeyAuth(api_url=BASE_URL, api_key="example-api-key")


def _cached_auth():
    auth = _auth()
    auth._token = "Bearer existing-token"
    return auth


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("status,error_type,code", ERROR_CASES)
@pytest.mark.parametrize("body", [b"", b"<html>Access denied</html>"])
def test_token_failure_preserves_http_error(
    asynchronous, status, error_type, code, body
):
    paths = []

    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(status, content=body)

    with pytest.raises(error_type) as raised:
        _request(handler, asynchronous, auth_factory=_auth)

    assert paths == ["/auth/token"]
    assert raised.value._status == status
    assert raised.value.content.code == code
    assert raised.value.content.message == (body.decode() or "Empty response body")


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("replay_status", [200, 401])
def test_cached_token_401_refreshes_and_replays_once(asynchronous, replay_status):
    requests = []

    def handler(request):
        requests.append((request.url.path, request.headers.get("Authorization")))
        if request.url.path == "/auth/token":
            return httpx.Response(
                200, json={"tokenType": "Bearer", "accessToken": "renewed-token"}
            )
        if len(requests) == 1:
            return httpx.Response(401, content=b"Authentication required")
        return httpx.Response(replay_status, content=b"Replayed response")

    if replay_status == 401:
        with pytest.raises(UnauthorizedError) as raised:
            _request(handler, asynchronous, auth_factory=_cached_auth)
        assert raised.value.content.message == "Replayed response"
    else:
        response = _request(handler, asynchronous, auth_factory=_cached_auth)
        assert response.status_code == 200
    assert requests == [
        ("/objects", "Bearer existing-token"),
        ("/auth/token", None),
        ("/objects", "Bearer renewed-token"),
    ]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_cached_token_403_does_not_refresh(asynchronous):
    paths = []

    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(403, content=b"Access denied")

    with pytest.raises(ForbiddenError):
        _request(handler, asynchronous, auth_factory=_cached_auth)

    assert paths == ["/objects"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_next_page_preserves_non_json_http_error(asynchronous):
    paths = []

    def handler(request):
        paths.append(str(request.url))
        if request.url.params.get("cursor") == "next":
            return httpx.Response(403, content=b"Access denied")
        return httpx.Response(
            200,
            json=[],
            headers={"Link": "<" + BASE_URL + '/objects?cursor=next>; rel="next"'},
        )

    with pytest.raises(ForbiddenError) as raised:
        _request(handler, asynchronous, paginate=True)

    assert raised.value.content.message == "Access denied"
    assert paths == [BASE_URL + "/objects", BASE_URL + "/objects?cursor=next"]

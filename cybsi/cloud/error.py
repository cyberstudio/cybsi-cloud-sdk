"""This section documents exceptions SDK can raise.

Those are exceptions SDK client can expect if SDK is used in correct way.
If your Python code didn't respect the expected model, there's no guarantees.
For example, if function argument types are ignored,
SDK can raise exceptions not listed here.

Each exception type is annotated if it makes sense to retry.

Some exceptions have ``code`` property. It allows to determine the concrete error.
"""
from typing import Any, Dict, Optional, cast

import httpx
from enum_tools import document_enum

from .enum import CybsiAPIEnum


class CybsiError(Exception):
    """Base exception used by SDK. Sometimes can be retried.

    If it's not of one of subclasses (see below), means unexpected error.

    :class:`CybsiError` covers those cases:

    * Unexpected API response status code. See :class:`APIError` for specific errors.
    * Unexpected API response content.
    * Connection error.

    """

    def __init__(self, message: str, ex: Optional[Exception] = None):
        if ex and str(ex) != "":
            message = f"{message}: {ex}"
        super().__init__(message)
        self._ex = ex


JsonObject = Dict[str, Any]


class APIError(CybsiError):
    """Base exception for HTTP 4xx API responses."""

    def __init__(
        self,
        status: int,
        content: JsonObject,
        header: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> None:
        self._status = status
        self._view = ErrorView(content)
        self._header = (
            header
            if header is not None
            else f"API response error. HTTP status: {self._status}"
        )
        self._suffix = (
            suffix
            if suffix is not None
            else f"code: {self._view.code}, message: {self._view.message}"
        )

        msg = self._header
        if self._suffix:
            msg += f", {self._suffix}"
        super().__init__(msg)

    @property
    def content(self) -> "ErrorView":
        return self._view


class InvalidRequestError(APIError):
    """Invalid request error. Retry will never work.

    Ideally, should not be raised by SDK. If it's raised, it means one of two things:

    * SDK was used incorrectly. For example, values of invalid type
      were passed to SDK functions.
    * There's a bug in request serialization in SDK. Please report the bug.

    """

    BadRequest = "BadRequest"
    InvalidData = "InvalidData"
    InvalidPathArgument = "InvalidPathArgument"
    InvalidQueryArgument = "InvalidQueryArgument"

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(400, resp.json(), header="invalid request")


class UnauthorizedError(APIError):
    """Client lacks valid authentication credentials. Retry will never work."""

    Unauthorized = "Unauthorized"

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(401, resp.json(), header="operation not authorized")


class ForbiddenError(APIError):
    """Operation was forbidden. Retry will not work unless system is reconfigured."""

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(403, resp.json(), header="operation forbidden")

    @property
    def code(self) -> "ForbiddenErrorCodes":
        """Error code."""
        return ForbiddenErrorCodes(self._view.code)


class NotFoundError(APIError):
    """Requested resource not found. Retry will never work."""

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(404, {}, header="resource not found", suffix="")


class ConflictError(APIError):
    """Resource already exists. Retry will never work."""

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(409, resp.json(), header="resource already exists")

    @property
    def code(self) -> "ConflictErrorCodes":
        """Error code."""
        return ConflictErrorCodes(self._view.code)


class ResourceModifiedError(APIError):
    """Resource was modified since last read. **Retry is a must**.

    Read the updated resource from API, and apply your modifications again.
    """

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(
            412, resp.json(), header="resource was modified since last read", suffix=""
        )


class RequestEntityTooLargeError(APIError):
    """Request content is too large."""

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(
            413, resp.json(), header="request content is too large", suffix=""
        )


class RangeNotSatisfiableError(APIError):
    def __init__(self, content: JsonObject) -> None:
        super().__init__(416, content, header="range is not satisfiable", suffix="")


class SemanticError(APIError):
    """Semantic error. Retry will not work (almost always).

    Request syntax was valid, but system business rules forbid the request.

    For example, we're trying to unpack an artifact, but the artifact is not an archive.
    """

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(422, resp.json(), header="semantic error")

    @property
    def code(self) -> "SemanticErrorCodes":
        """Error code."""
        return SemanticErrorCodes(self._view.code)


class TooManyRequestsError(APIError):
    """Too many requests error.

    Retry request after some time.
    """

    def __init__(self, resp: httpx.Response) -> None:
        super().__init__(429, resp.json(), header="too many requests error")
        retry_after = resp.headers.get("Retry-After")
        self._retry_after = int(retry_after) if retry_after is not None else None

    @property
    def code(self) -> "TooManyRequestsErrorCodes":
        """Error code."""
        return TooManyRequestsErrorCodes(self._view.code)

    @property
    def retry_after(self) -> Optional[int]:
        """Period in seconds after which request could be repeated."""
        return self._retry_after


@document_enum
class ForbiddenErrorCodes(CybsiAPIEnum):
    """Possible error codes of :class:`ForbiddenError`."""

    MissingPermissions = "MissingPermissions"
    """Authenticated but not authorized to perform operation."""
    Forbidden = "Forbidden"
    """Other cases."""


@document_enum
class ConflictErrorCodes(CybsiAPIEnum):
    """Conflict error codes."""

    DuplicateSchema = "DuplicateSchema"
    """Schema with the given schemaID is already registered."""
    DuplicateCollection = "DuplicateCollection"
    """Collection with the given name is already registered."""


@document_enum
class SemanticErrorCodes(CybsiAPIEnum):
    """Semantic error codes."""

    ResourceNotFound = "ResourceNotFound"
    """Cloud resource not found."""
    InvalidSchemaID = "InvalidSchemaID"
    """schemaID parameter can't be changed."""
    SchemaNotFound = "SchemaNotFound"
    """The specified schema is not found"""
    InvalidRequestLimit = "InvalidRequestLimit"
    """The specified request limit cannot be set."""
    LimitSetConflict = "LimitSetConflict"
    """The limit set has conflicts."""

    # Objects
    InvalidKeyFormat = "InvalidKeyFormat"
    """Object key has invalid format."""
    InvalidKeySet = "InvalidKeySet"
    """Object has invalid key set."""
    KeySetConflict = "KeySetConflict"
    """Object key intersects with another one."""
    SchemaCheckFail = "SchemaCheckFail"
    """Object validation by schema failed."""
    CursorOutOfRange = "CursorOutOfRange"
    """Cursor for collection changes is obsolete."""
    InvalidFilePart = "InvalidFilePart"
    """File part is invalid"""
    MissingFilePart = "MissingFilePart"
    """File part is missing"""

    # Filebox
    FileNotFound = "FileNotFound"
    """File not found."""

    # Tasks
    TaskNotFound = "TaskNotFound"
    """Task not found."""
    InvalidState = "InvalidState"
    """Invalid task state."""


@document_enum
class TooManyRequestsErrorCodes(CybsiAPIEnum):
    """Too many requests error codes."""

    LimitExceeded = "LimitExceeded"
    """Request limit exceeded."""


class ErrorView(dict):
    """Error returned by Cybsi Cloud API."""

    @property
    def code(self) -> str:
        """Error code."""

        return cast(str, self.get("code"))

    @property
    def message(self) -> str:
        """Error message."""

        return cast(str, self.get("message"))

    @property
    def details(self) -> JsonObject:
        """Error details."""

        return cast(JsonObject, self.get("details"))


class SchemaCheckErrorDetails(dict):
    """Details for schema check error."""

    @property
    def absolute_keyword_location(self) -> str:
        """Absolute validation path of validating schema."""

        return cast(str, self.get("AbsoluteKeywordLocation"))

    @property
    def instance_location(self) -> str:
        """Location of the json value within the instance being validated."""

        return cast(str, self.get("InstanceLocation"))

    @property
    def message(self) -> str:
        """Error description."""

        return cast(str, self.get("Message"))


_error_mapping = {
    400: InvalidRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    412: ResourceModifiedError,
    413: RequestEntityTooLargeError,
    416: RangeNotSatisfiableError,
    422: SemanticError,
    429: TooManyRequestsError,
}


def _raise_cybsi_error(resp: httpx.Response) -> None:
    err_cls = _error_mapping.get(resp.status_code, None)
    if err_cls is not None:
        raise err_cls(resp)

    raise CybsiError(
        f"unexpected response status code: {resp.status_code}. "
        f"Request body: {resp.text}"
    )

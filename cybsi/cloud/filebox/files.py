import uuid
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Tuple

from httpx import Response

from ..error import CybsiError
from ..internal import BaseAPI, BaseAsyncAPI, JsonObjectView
from ..internal.buffer import (
    AsyncBufferedReader,
    AsyncBytesReader,
    AsyncLimitedReader,
    BufferedReader,
    BytesReader,
    LimitedReader,
)
from ..internal.multipart import AsyncStreamWrapper

MB = 1 << 20
_DEFAULT_PART_SIZE = 5 * MB
_MULTIPART_UPLOAD_MAX_SIZE = 50 * MB
_DEFAULT_BUF_SIZE = 65536

_FILES_PATH = "filebox/files"
_SESSIONS_PATH = "filebox/sessions"

_CONTENT_RANGE_HEADER = "Content-Range"
_CONTENT_LENGTH_HEADER = "Content-Length"
_RANGE_HEADER = "Range"


class FilesAPI(BaseAPI):
    """Files API."""

    def upload(self, data: BytesReader, *, name: str, size: int = -1) -> "FileRefView":
        """Upload a file.

        The maximum file size is 1GiB.

        Note:
            Calls `PUT /filebox/files`.
        Args:
            data (bytes): The data of the file.
            name (str): The name of the file.
            size (int): The size of the file.
        Return:
            The reference to the uploaded file.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.RequestEntityTooLargeError`:
                Provided file data is too large.
        """

        if size <= 0 or size > _MULTIPART_UPLOAD_MAX_SIZE:
            return self._upload_file_by_parts(data, size=size)

        form = {"file": (name, data)}
        r = self._connector.do_put(_FILES_PATH, files=form, stream=True)
        r.read()  # in stream mode we need to read the body before use json().

        return FileRefView(r.json())

    def _upload_file_by_parts(
        self, data: BytesReader, *, size: int = -1
    ) -> "FileRefView":
        part_size = _DEFAULT_PART_SIZE
        session = self.create_session(part_size=part_size)

        parts = _iter_parts(data, part_size=part_size, total_size=size)
        for part_num, (part, part_size) in enumerate(parts, start=1):
            self.upload_session_part(
                part, session_id=session.id, part_number=part_num, size=part_size
            )

        return self.complete_session(session_id=session.id)

    def get_file_size(self, file_id: uuid.UUID) -> int:
        """Get a file size.

        Note:
            Calls `HEAD /filebox/files/{fileID}/content`.
        Args:
            file_id: The file identifier.
        Return:
            The file size in bytes.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
        """

        r = self._connector.do_head(f"{_FILES_PATH}/{file_id}/content")
        size = r.headers.get(_CONTENT_LENGTH_HEADER).strip()
        if size:
            return int(size)
        return 0

    def create_session(self, part_size: int) -> "SessionRefView":
        """Create an upload session.

        Note:
            Calls `POST /filebox/sessions`.
        Args:
            part_size: The size of file parts.
        Return:
            The reference to the created session.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """

        body = {"partSize": part_size}
        r = self._connector.do_post(path=_SESSIONS_PATH, json=body)
        return SessionRefView(r.json())

    def upload_session_part(
        self, part: BytesReader, *, session_id: uuid.UUID, part_number, size: int
    ):
        """Upload the file part.

        Note:
            Calls `POST /filebox/sessions/{sessionID}/parts`.
        Args:
            part: The file part data.
            session_id: The identifier of the upload session.
            part_number: The part number.
            size: The part size.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
            :class:`~cybsi.cloud.error.RequestEntityTooLargeError`:
                Provided file data is too large.
        """

        path = f"{_SESSIONS_PATH}/{session_id}/parts"
        form = {
            "number": str(part_number),
            "partSize": str(size),
            "filePart": part,
        }

        self._connector.do_put(path, files=form)

    def complete_session(self, session_id: uuid.UUID) -> "FileRefView":
        """Complete the session.

        Note:
            Calls `POST /filebox/sessions/{sessionID}/completed`.
        Args:
            session_id: The identifier of the upload session.
        Return:
            The reference to the uploaded file.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
            :class:`~cybsi.cloud.error.SemanticError`: Semantic request error.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidFilePart`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidFilePart`
        """

        path = f"{_SESSIONS_PATH}/{session_id}/completed"
        r = self._connector.do_post(path=path)
        return FileRefView(r.json())

    def download_part(
        self, file_id: uuid.UUID, *, start: int, end: int
    ) -> "FileContent":
        """Download a file part.

        The byte numeration start with 0.
        The maximum part size (end-start) is 50 MiB.

        Note:
            Calls `GET /filebox/files/{fileID}/content`.
        Args:
            file_id: The file identifier.
            start: The part start byte number.
            end: The part end byte number.
        Return:
            The file part content.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
            :class:`~cybsi.cloud.error.RangeNotSatisfiableError`:
                The requested content range could not be satisfied.
        """

        headers = {_RANGE_HEADER: f"bytes={start}-{end}"}
        part = self._connector.do_get(
            path=f"{_FILES_PATH}/{file_id}/content", headers=headers, stream=True
        )
        return FileContent((p for p in [part]))

    def download(self, file_id: uuid.UUID) -> "FileContent":
        """Download a file entirely.

        Note:
            Calls `GET /filebox/files/{fileID}/content`.
        Args:
            file_id: The file identifier.
        Return:
            The file content.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
        """

        headers = {_RANGE_HEADER: f"bytes=0-{_DEFAULT_PART_SIZE}"}
        first_part = self._connector.do_get(
            path=f"{_FILES_PATH}/{file_id}/content", headers=headers, stream=True
        )

        def parts_iter() -> Iterator[Response]:
            content_range: str = first_part.headers.get(_CONTENT_RANGE_HEADER)
            start, end, size = _parse_content_range(content_range)

            yield first_part

            bytes_read = end - start + 1
            while bytes_read < size:
                start, end = end + 1, end + _DEFAULT_PART_SIZE
                h = {"Range": f"bytes={start}-{end}"}
                part = self._connector.do_get(
                    path=f"{_FILES_PATH}/{file_id}/content", headers=h, stream=True
                )
                yield part
                start, end, _ = _parse_content_range(
                    part.headers.get(_CONTENT_RANGE_HEADER)
                )
                bytes_read += end - start + 1

        return FileContent(parts_iter())


class FilesAsyncAPI(BaseAsyncAPI):
    """Files asynchronous API"""

    async def upload(
        self, data: AsyncBytesReader, *, name: str, size: int = -1
    ) -> "FileRefView":
        """Upload a file.

        The maximum file size is 1GiB.

        Note:
            Calls `PUT /filebox/files`.
        Args:
            data (bytes): The data of the file.
            name (str): The name of the file.
            size (int): The size of the file.
        Return:
            The reference to the uploaded file.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.RequestEntityTooLargeError`:
                Provided file data is too large.
        """

        if size <= 0 or size > _MULTIPART_UPLOAD_MAX_SIZE:
            return await self._upload_file_by_parts(data, name=name, size=size)

        form: Dict[str, Any] = {"file": (name, AsyncStreamWrapper(data, size))}
        r = await self._connector.do_put(_FILES_PATH, files=form, stream=True)
        await r.aread()  # in stream mode we need to read before use json().

        return FileRefView(r.json())

    async def _upload_file_by_parts(
        self, data: AsyncBytesReader, *, name: str, size: int = -1
    ) -> "FileRefView":
        session = await self.create_session(part_size=_DEFAULT_PART_SIZE)
        parts = _aiter_parts(data, part_size=_DEFAULT_PART_SIZE, total_size=size)

        part_num = 0
        async for part, part_size in parts:
            part_num += 1
            await self.upload_session_part(
                part, session_id=session.id, part_number=part_num, size=part_size
            )

        return await self.complete_session(session_id=session.id)

    async def get_file_size(self, file_id: uuid.UUID) -> int:
        """Get a file size.

        Note:
            Calls `HEAD /filebox/files/{fileID}/content`.
        Args:
            file_id: The file identifier.
        Return:
            The file size in bytes.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
        """

        r = await self._connector.do_head(f"{_FILES_PATH}/{file_id}/content")
        size = r.headers.get(_CONTENT_LENGTH_HEADER).strip()
        if size:
            return int(size)
        return 0

    async def download_part(
        self, file_id: uuid.UUID, *, start: int, end: int
    ) -> "FileAsyncContent":
        """Download a file part.

        The byte numeration start with 0.
        The maximum part size (end-start) is 50 MiB.

        Note:
            Calls `GET /filebox/files/{fileID}/content`.
        Args:
            file_id: The file identifier.
            start: The part start byte number.
            end: The part end byte number.
        Return:
            The file part content.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
            :class:`~cybsi.cloud.error.RangeNotSatisfiableError`:
                The requested content range could not be satisfied.
        """

        headers = {_RANGE_HEADER: f"bytes={start}-{end}"}
        part = await self._connector.do_get(
            path=f"{_FILES_PATH}/{file_id}/content", headers=headers, stream=True
        )

        async def part_gen():
            yield part

        return FileAsyncContent(part_gen())

    async def create_session(self, part_size: int) -> "SessionRefView":
        """Create an upload session.

        Note:
            Calls `POST /filebox/sessions`.
        Args:
            part_size: The size of file parts.
        Return:
            The reference to the created session.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """

        body = {"partSize": part_size}
        r = await self._connector.do_post(path=_SESSIONS_PATH, json=body)
        return SessionRefView(r.json())

    async def upload_session_part(
        self, part: AsyncBytesReader, *, session_id: uuid.UUID, part_number, size: int
    ):
        """Upload the file part.

        Note:
            Calls `POST /filebox/sessions/{sessionID}/parts`.
        Args:
            part: The file part data.
            session_id: The identifier of the upload session.
            part_number: The part number.
            size: The part size.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
            :class:`~cybsi.cloud.error.RequestEntityTooLargeError`:
                Provided file data is too large.
        """

        path = f"{_SESSIONS_PATH}/{session_id}/parts"
        form = {
            "number": str(part_number),
            "partSize": str(size),
            "filePart": AsyncStreamWrapper(part, size),
        }
        await self._connector.do_put(path, files=form)

    async def complete_session(self, session_id: uuid.UUID) -> "FileRefView":
        """Complete the session.

        Note:
            Calls `POST /filebox/sessions/{sessionID}/completed`.
        Args:
            session_id: The identifier of the upload session.
        Return:
            The reference to the uploaded file.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
            :class:`~cybsi.cloud.error.SemanticError`: Semantic request error.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidFilePart`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidFilePart`
        """

        path = f"{_SESSIONS_PATH}/{session_id}/completed"
        r = await self._connector.do_post(path=path)
        return FileRefView(r.json())

    async def download(self, file_id: uuid.UUID) -> "FileAsyncContent":
        """Download a file entirely.

        Note:
            Calls `GET /filebox/files/{fileID}/content`.
        Args:
            file_id: The file identifier.
        Return:
            The file content.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.NotFoundError`: File not found.
        """

        headers = {_RANGE_HEADER: f"bytes=0-{_DEFAULT_PART_SIZE}"}
        first_part = await self._connector.do_get(
            path=f"{_FILES_PATH}/{file_id}/content", headers=headers, stream=True
        )

        async def parts_iter() -> AsyncIterator[Response]:
            content_range: str = first_part.headers.get(_CONTENT_RANGE_HEADER)
            start, end, size = _parse_content_range(content_range)

            yield first_part

            bytes_read = end - start + 1
            while bytes_read < size:
                start, end = end + 1, end + _DEFAULT_PART_SIZE
                h = {"Range": f"bytes={start}-{end}"}
                chunk = await self._connector.do_get(
                    path=f"{_FILES_PATH}/{file_id}/content", headers=h, stream=True
                )
                yield chunk

                start, end, _ = _parse_content_range(
                    chunk.headers.get(_CONTENT_RANGE_HEADER)
                )
                bytes_read += end - start + 1

        return FileAsyncContent(parts_iter())


class FileAsyncContent:
    """File asynchronous content."""

    def __init__(self, parts: AsyncIterator[Response]):
        self._parts = parts
        self._current_part: Optional[Response] = None
        self._bytes_iter: Optional[AsyncIterator[bytes]] = None
        self._buffer: bytes = b""

    async def read(self, n: int = 0) -> bytes:
        """Read at most n bytes of the content.

        Return a bytestring containing the bytes read.
        If the end of the content is reached, an empty bytes object is returned.
        If n <= 0 it returns the whole content.
        """

        if n <= 0:
            return await self._readall()

        if self._bytes_iter is None:
            self._bytes_iter = self._iter_chunked()

        if len(self._buffer) >= n:
            result = self._buffer[:n]
            self._buffer = self._buffer[n:]
            return result

        try:
            chunk = await self._bytes_iter.__anext__()
        except StopAsyncIteration:
            result = self._buffer[:]
            self._buffer = b""
            return result

        if not self._buffer and len(chunk) <= n:
            return chunk

        rest = n - len(self._buffer)
        if rest > len(chunk):
            result = b"".join((self._buffer, chunk))
            self._buffer = b""
        else:
            result = b"".join((self._buffer, chunk[:rest]))
            self._buffer = chunk[rest:]

        return result

    async def _readall(self) -> bytes:
        """Read the content entirely."""
        chunks = []
        self._bytes_iter = self._iter_chunked()
        async for buf in self._bytes_iter:
            chunks.append(buf)
        return b"".join(chunks)

    def _iter_chunked(self, size=_DEFAULT_BUF_SIZE) -> AsyncIterator[bytes]:
        """A byte-iterator over the file content."""

        async def chunk_iterator() -> AsyncIterator[bytes]:
            async for p in self._parts:
                self._current_part = p
                async for buf in p.aiter_bytes(size):
                    yield buf

        return chunk_iterator()

    async def __aenter__(self) -> "FileAsyncContent":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._current_part is not None:
            await self._current_part.aclose()


class FileContent:
    """File content."""

    def __init__(self, parts: Iterator[Response]):
        self._parts = parts
        self._current_part: Optional[Response] = None
        self._bytes_iter: Optional[Iterator[bytes]] = None
        self._buffer: bytes = b""

    def read(self, n: int = 0) -> bytes:
        """Read at most n bytes of the content.

        Return a bytestring containing the bytes read.

        If the end of the content is reached, an empty bytes object is returned.
        If n <= 0 it returns the whole content.
        """

        if n <= 0:
            return self._readall()

        if self._bytes_iter is None:
            self._bytes_iter = self._iter_chunked()

        if len(self._buffer) >= n:
            result = self._buffer[:n]
            self._buffer = self._buffer[n:]
            return result

        try:
            chunk = next(self._bytes_iter)
        except StopIteration:
            result = self._buffer[:]
            self._buffer = b""
            return result

        if not self._buffer and len(chunk) <= n:
            return chunk

        rest = n - len(self._buffer)
        if rest > len(chunk):
            result = b"".join((self._buffer, chunk))
            self._buffer = b""
        else:
            result = b"".join((self._buffer, chunk[:rest]))
            self._buffer = chunk[rest:]

        return result

    def _readall(self) -> bytes:
        """Read the content entirely."""
        chunks = []
        self._bytes_iter = self._iter_chunked()
        for buf in self._bytes_iter:
            chunks.append(buf)
        return b"".join(chunks)

    def _iter_chunked(self, size=_DEFAULT_BUF_SIZE) -> Iterator[bytes]:
        """A byte-iterator over the file content."""

        def chunk_iterator() -> Iterator[bytes]:
            for p in self._parts:
                self._current_part = p
                for buf in p.iter_bytes(size):
                    yield buf

        return chunk_iterator()

    def __enter__(self) -> "FileContent":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._current_part is not None:
            self._current_part.close()


class FileRefView(JsonObjectView):
    """File reference view."""

    @property
    def id(self) -> uuid.UUID:
        """File ID."""
        return uuid.UUID(self._get("fileID"))


class SessionRefView(JsonObjectView):
    """Upload session reference view."""

    @property
    def id(self) -> uuid.UUID:
        """Session ID."""
        return uuid.UUID(self._get("sessionID"))


def _parse_content_range(header: str) -> Tuple[int, int, int]:
    header = header.strip()
    bytes_prefix = "bytes"
    if not header.startswith(bytes_prefix):
        raise CybsiError("invalid content range header")
    bytes_prefix_len = len(bytes_prefix)
    header = header[bytes_prefix_len:].strip()

    content_range, size = header.split("/", maxsplit=1)
    start, end = content_range.split("-", maxsplit=1)
    try:
        return int(start.strip()), int(end.strip()), int(size.strip())
    except ValueError as exp:
        raise CybsiError("invalid content range") from exp


def _iter_parts(
    source: BytesReader, part_size: int, total_size=-1
) -> Iterator[Tuple[BytesReader, int]]:
    # if total size is not specified the buffer size would be equal to part size.
    buf_size = 1 if total_size > 0 else part_size
    buf = BufferedReader(source, size=buf_size)

    part_number = 0
    while peeked := buf.peek(buf_size):
        if total_size < 0:
            size = len(peeked)
            yield LimitedReader(buf, limit=size), size
        else:
            part_number += 1
            rest = total_size - (part_number * part_size)
            size = part_size if rest > 0 else total_size % part_size
            yield LimitedReader(buf, limit=size), size


async def _aiter_parts(
    source: AsyncBytesReader, part_size: int, total_size=-1
) -> AsyncIterator[Tuple[AsyncBytesReader, int]]:
    # if total size is not specified the buffer size would be equal to part size.
    buf_size = 1 if total_size > 0 else part_size
    buf = AsyncBufferedReader(source, size=buf_size)

    part_number = 0
    while peeked := (await buf.peek(buf_size)):
        if total_size < 0:
            size = len(peeked)
            yield AsyncLimitedReader(buf, limit=size), size
        else:
            part_number += 1
            rest = total_size - (part_number * part_size)
            size = part_size if rest > 0 else total_size % part_size
            yield AsyncLimitedReader(buf, limit=size), size

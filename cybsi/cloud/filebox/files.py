import uuid
from abc import abstractmethod
from typing import AsyncIterator, Iterator, Optional, Protocol, Tuple

from httpx import Response

from ..error import CybsiError
from ..internal import BaseAPI, BaseAsyncAPI, JsonObjectView

_PATH = "filebox/files"
_DEFAULT_PART_SIZE = 10 * (1 << 20)  # 10 Mb
_DEFAULT_BUF_SIZE = 65536

_CONTENT_RANGE_HEADER = "Content-Range"
_CONTENT_LENGTH_HEADER = "Content-Length"
_RANGE_HEADER = "Range"


class FilesAPI(BaseAPI):
    """Files API."""

    def upload(self, data: "BytesReader", *, name: str) -> "FileRefView":
        """Upload a file.

        The maximum file size allowed is 50 MiB.

        Note:
            Calls `PUT /filebox/files`.
        Args:
            data (bytes): The data of the file.
            name (str): The name of the file.
        Return:
            The reference to the uploaded file.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.RequestEntityTooLargeError`:
                Provided file data is too large.
        """

        files = {"file": (name, data)}
        r = self._connector.do_put(_PATH, files=files, stream=True)
        r.read()  # in stream mode we need to read before use json().

        return FileRefView(r.json())

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

        r = self._connector.do_head(f"{_PATH}/{file_id}/content")
        size = r.headers.get(_CONTENT_LENGTH_HEADER).strip()
        if size:
            return int(size)
        return 0

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
            path=f"{_PATH}/{file_id}/content", headers=headers, stream=True
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
            path=f"{_PATH}/{file_id}/content", headers=headers, stream=True
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
                    path=f"{_PATH}/{file_id}/content", headers=h, stream=True
                )
                yield part
                start, end, _ = _parse_content_range(
                    part.headers.get(_CONTENT_RANGE_HEADER)
                )
                bytes_read += end - start + 1

        return FileContent(parts_iter())


class FilesAsyncAPI(BaseAsyncAPI):
    """Files asynchronous API"""

    async def upload(self, data: "BytesReader", *, name: str) -> "FileRefView":
        """Upload a file.

        The maximum file size allowed is 50 MiB.

        Note:
            Calls `PUT /filebox/files`.
        Args:
            data (bytes): The data of the file.
            name (str): The name of the file.
        Return:
            The reference to the uploaded file.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.RequestEntityTooLargeError`:
                Provided file data is too large.
        """

        files = {"file": (name, data)}
        r = await self._connector.do_put(_PATH, files=files, stream=True)
        await r.aread()  # in stream mode we need to read before use json().

        return FileRefView(r.json())

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

        r = await self._connector.do_head(f"{_PATH}/{file_id}/content")
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
            path=f"{_PATH}/{file_id}/content", headers=headers, stream=True
        )

        async def part_gen():
            yield part

        return FileAsyncContent(part_gen())

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
            path=f"{_PATH}/{file_id}/content", headers=headers, stream=True
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
                    path=f"{_PATH}/{file_id}/content", headers=h, stream=True
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
        return self._get("fileID")


class BytesReader(Protocol):
    """Describes a bytes reader protocol"""

    @abstractmethod
    def read(self, *args, **kwargs) -> bytes:
        """Read bytes."""
        ...


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

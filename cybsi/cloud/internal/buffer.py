import io
from typing import Protocol

_DEFAULT_BUF_SIZE = 65536


class BytesReader(Protocol):
    """Describes bytes reader protocol."""

    def read(self, *args, **kwargs) -> bytes:
        """Read bytes."""
        ...


class AsyncBytesReader(Protocol):
    """Describes asynchronous bytes reader protocol."""

    async def read(self, *args, **kwargs) -> bytes:
        """Read bytes."""
        ...


class BufferedReader:
    """Buffered byte reader."""

    def __init__(self, source: BytesReader, *, size: int):
        self._source = source
        self._buf = io.BytesIO()
        self._buf_size = size
        self._r = 0  # read position
        self._w = 0  # write position

    @property
    def _buffered(self) -> int:
        return self._w - self._r

    def _readall(self) -> bytes:
        result = io.BytesIO(b"")
        chunk = self.read(_DEFAULT_BUF_SIZE)
        while chunk:
            result.write(chunk)
            chunk = self.read(_DEFAULT_BUF_SIZE)
        return result.getvalue()

    def read(self, n: int = -1) -> bytes:
        """Read at most n bytes from the source.

        Return a bytestring containing the bytes read.

        If the end of the data is reached, an empty bytes object is returned.
        If n <= 0 it returns the whole data.
        """

        if n <= 0:
            return self._readall()

        if self._buffered == 0:
            return self._source.read(n)

        chunk = self._buf.read(min(n, self._buffered))
        self._r += len(chunk)

        if self._buffered == 0 and len(chunk) < n:
            rest = n - len(chunk)
            chunk += self._source.read(rest)

        return chunk

    def peek(self, n: int) -> bytes:
        """Peeks the next n bytes without advancing the reader.

        Returns a bytestring containing the bytes peeked.

        If n <= 0 it returns the empty bytestring.
        If n is greater than the buffer size it returns the buffered bytes.
        """

        if n <= 0:
            return b""

        n = self._buf_size if n > self._buf_size else n

        buffered: int = self._buffered
        if buffered >= n:
            # enough data in buffer.
            start, end = self._r, self._r + n
            return bytes(self._buf.getbuffer()[start:end])

        pos = buffered
        if self._r == self._w:
            # buffer is read, reset buffer.
            self._r, self._w = 0, 0
            pos = 0
        if self._r > 0:
            # move non-read data to the zero position
            view = self._buf.getbuffer()
            start, end = self._r, self._w
            view[0:pos] = view[start:end]
            # delete the memory view object otherwise
            # it would be impossible to write to the buffer
            del view
            self._r, self._w = 0, pos
        self._buf.seek(pos)

        while (rest := n - self._buffered) > 0:
            chunk_size = min(_DEFAULT_BUF_SIZE, rest)
            chunk = self._source.read(chunk_size)
            if not chunk:
                break
            self._buf.write(chunk)
            self._w += len(chunk)

        self._buf.seek(0)
        start, end = self._r, self._w
        return bytes(self._buf.getbuffer()[start:end])


class AsyncBufferedReader:
    """Asynchronous buffered byte reader."""

    def __init__(self, source: AsyncBytesReader, *, size: int):
        self._source = source
        self._buf = io.BytesIO()
        self._buf_size = size
        self._r = 0  # read position
        self._w = 0  # write position

    @property
    def _buffered(self) -> int:
        return self._w - self._r

    async def _readall(self) -> bytes:
        result = io.BytesIO(b"")
        chunk = await self.read(_DEFAULT_BUF_SIZE)
        while chunk:
            result.write(chunk)
            chunk = await self.read(_DEFAULT_BUF_SIZE)
        return result.getvalue()

    async def read(self, n: int = -1) -> bytes:
        """Read at most n bytes from the source.

        Return a bytestring containing the bytes read.

        If the end of the data is reached, an empty bytes object is returned.
        If n <= 0 it returns the whole data.
        """

        if n <= 0:
            return await self._readall()

        if self._buffered == 0:
            return await self._source.read(n)

        chunk = self._buf.read(min(n, self._buffered))
        self._r += len(chunk)

        if self._buffered == 0 and len(chunk) < n:
            rest = n - len(chunk)
            chunk += await self._source.read(rest)

        return chunk

    async def peek(self, n: int) -> bytes:
        """Peeks the next n bytes without advancing the reader.

        Returns a bytestring containing the bytes peeked.

        If n <= 0 it returns the empty bytestring.
        If n is greater than the buffer size it returns the buffered bytes.
        """

        if n <= 0:
            return b""

        n = self._buf_size if n > self._buf_size else n

        buffered: int = self._buffered
        if buffered >= n:
            # enough data in buffer.
            start, end = self._r, self._r + n
            return bytes(self._buf.getbuffer()[start:end])

        pos = buffered
        if self._r == self._w:
            # buffer is read, reset buffer.
            self._r, self._w = 0, 0
            pos = 0
        if self._r > 0:
            # move non-read data to the zero position.
            view = self._buf.getbuffer()
            start, end = self._r, self._w
            view[0:pos] = view[start:end]
            # delete the memory view object otherwise
            # it would be impossible to write to the buffer
            del view
            self._r, self._w = 0, pos
        self._buf.seek(pos)

        while (rest := n - self._buffered) > 0:
            chunk_size = min(_DEFAULT_BUF_SIZE, rest)
            chunk = await self._source.read(chunk_size)
            if not chunk:
                break
            self._buf.write(chunk)
            self._w += len(chunk)

        self._buf.seek(0)
        start, end = self._r, self._w
        return bytes(self._buf.getbuffer()[start:end])


class LimitedReader:
    """Limited byte reader."""

    def __init__(self, source: BytesReader, *, limit: int):
        self._source = source
        self._limit = limit
        self._byte_read = 0

    def _readall(self) -> bytes:
        result = io.BytesIO(b"")
        chunk = self.read(_DEFAULT_BUF_SIZE)
        while chunk:
            result.write(chunk)
            chunk = self.read(_DEFAULT_BUF_SIZE)
        return result.getvalue()

    def read(self, n: int = -1) -> bytes:
        """Read at most n bytes from the source.

        Return a bytestring containing the bytes read.

        If the end of the data is reached, an empty bytes object is returned.
        If n <= 0 it returns the whole data.
        """

        if n <= 0:
            return self._readall()

        if self._byte_read == self._limit:
            return b""

        rest = self._limit - self._byte_read
        n = min(n, rest)
        chunk = self._source.read(n)
        self._byte_read += len(chunk)
        return chunk


class AsyncLimitedReader:
    """Asynchronous limited byte reader."""

    def __init__(self, source: AsyncBytesReader, *, limit: int):
        self._source = source
        self._limit = limit
        self._byte_read = 0

    async def _readall(self) -> bytes:
        result = io.BytesIO(b"")
        chunk = await self.read(_DEFAULT_BUF_SIZE)
        while chunk:
            result.write(chunk)
            chunk = await self.read(_DEFAULT_BUF_SIZE)
        return result.getvalue()

    async def read(self, n: int = -1) -> bytes:
        """Read at most n bytes from the source.

        Return a bytestring containing the bytes read.

        If the end of the data is reached, an empty bytes object is returned.
        If n <= 0 it returns the whole data.
        """

        if n <= 0:
            return await self._readall()

        if self._byte_read == self._limit:
            return b""

        rest = self._limit - self._byte_read
        n = min(n, rest)
        chunk = await self._source.read(n)
        self._byte_read += len(chunk)
        return chunk

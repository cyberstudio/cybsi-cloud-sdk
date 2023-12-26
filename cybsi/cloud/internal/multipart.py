"""
See https://github.com/encode/httpx/issues/1620

If you need to upload async stream as a multipart `files` argument,
you need to apply this patch and wrap stream with `AsyncStreamWrapper`::
"""
from typing import AsyncIterator, Optional

from httpx import _content
from httpx._multipart import FileField, MultipartStream
from httpx._types import RequestFiles

from cybsi.cloud.internal.buffer import AsyncBytesReader


class AsyncStreamWrapper:
    def __init__(self, stream: AsyncBytesReader, size: int):
        self.stream = stream
        self.size = size


class AsyncAwareMultipartStream(MultipartStream):
    def __init__(
        self, data: dict, files: RequestFiles, boundary: Optional[bytes] = None
    ) -> None:
        super().__init__(data, files, boundary)
        for field in self.fields:
            if isinstance(field, FileField) and isinstance(
                field.file, AsyncStreamWrapper
            ):
                field.get_length = lambda f=field: len(f.render_headers()) + f.file.size  # type: ignore # noqa: E501

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for field in self.fields:
            yield b"--%s\r\n" % self.boundary
            if isinstance(field, FileField) and isinstance(
                field.file, AsyncStreamWrapper
            ):
                yield field.render_headers()
                chunk_size = 4096
                while chunk := (await field.file.stream.read(chunk_size)):
                    yield chunk
            else:
                for chunk in field.render():
                    yield chunk
            yield b"\r\n"
        yield b"--%s--\r\n" % self.boundary


def apply_async_multipart_stream():
    _content.MultipartStream = AsyncAwareMultipartStream

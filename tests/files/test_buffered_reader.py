import io
import unittest

from cybsi.cloud.files import BufferedReader, AsyncBufferedReader


class BufferedReaderTest(unittest.TestCase):
    def test_buffer_size_is_equal_to_data_size(self):
        expected = b"test"
        size = len(expected)
        buf = BufferedReader(io.BytesIO(expected), size=size)

        actual = buf.peek(size)
        self.assertEqual(expected, actual)
        self.assertEqual(expected, buf.read())

    def test_buffer_size_is_greater_than_data_size(self):
        expected = b"test"
        size = len(expected)+1
        buf = BufferedReader(io.BytesIO(expected), size=size)

        actual = buf.peek(size)
        self.assertEqual(expected, actual)
        self.assertEqual(expected, buf.read())

    def test_read_size_is_a_multiple_of_data_size(self):
        expected = b"test"
        size, n = 4, 2
        buf = BufferedReader(io.BytesIO(expected), size=size)

        actual = b""
        while buf.peek(n) != b"":
            actual += buf.read(n)

        self.assertEqual(expected, actual)
        rest = buf.read()
        self.assertEqual(b"", rest)

    def test_read_size_is_a_not_multiple_of_data_size(self):
        expected = b"test"
        size, n = 4, 3
        buf = BufferedReader(io.BytesIO(expected), size=size)

        actual = b""
        while buf.peek(n) != b"":
            actual += buf.read(n)

        self.assertEqual(expected, actual)
        rest = buf.read()
        self.assertEqual(b"", rest)

    def test_read_size_is_greater_than_buffer_size(self):
        expected = b"testdata"
        size = 4
        buf = BufferedReader(io.BytesIO(expected), size=size)
        buf.peek(size)

        actual = b""
        while chunk := buf.read(len(expected)):
            actual += chunk

        self.assertEqual(expected, actual)

    def test_read_all_data(self):
        expected = b"testdata"
        size = 4
        buf = BufferedReader(io.BytesIO(expected), size=size)
        buf.peek(size) # put some data to buffer

        actual = buf.read()
        self.assertEqual(expected, actual)


class AsyncBufferedReaderTest(unittest.IsolatedAsyncioTestCase):

    class AsyncReader:
        def __init__(self, data: bytes):
            self._buf = io.BytesIO(data)

        async def read(self, n: int = -1):
            return self._buf.read(n)

    async def test_buffer_size_is_equal_to_data_size(self):
        expected = b"test"
        size = len(expected)
        buf = AsyncBufferedReader(self.AsyncReader(expected), size=size)

        actual = await buf.peek(size)
        self.assertEqual(expected, actual)
        self.assertEqual(expected, await buf.read())

    async def test_buffer_size_is_greater_than_data_size(self):
        expected = b"test"
        size = len(expected)+1
        buf = AsyncBufferedReader(self.AsyncReader(expected), size=size)

        actual = await buf.peek(size)
        self.assertEqual(expected, actual)
        self.assertEqual(expected, await buf.read())

    async def test_read_size_is_a_multiple_of_data_size(self):
        expected = b"test"
        size, n = 4, 2
        buf = AsyncBufferedReader(self.AsyncReader(expected), size=size)

        actual = b""
        while await buf.peek(n) != b"":
            actual += await buf.read(n)

        self.assertEqual(expected, actual)
        rest = await buf.read()
        self.assertEqual(b"", rest)

    async def test_read_size_is_a_not_multiple_of_data_size(self):
        expected = b"test"
        size, n = 4, 3
        buf = AsyncBufferedReader(self.AsyncReader(expected), size=size)

        actual = b""
        while await buf.peek(n) != b"":
            actual += await buf.read(n)

        self.assertEqual(expected, actual)
        rest = await buf.read()
        self.assertEqual(b"", rest)

    async def test_read_size_is_greater_than_buffer_size(self):
        expected = b"testdata"
        size = 4
        buf = AsyncBufferedReader(self.AsyncReader(expected), size=size)
        await buf.peek(size)

        actual = b""
        while chunk := await buf.read(len(expected)):
            actual += chunk

        self.assertEqual(expected, actual)

    async def test_read_all_data(self):
        expected = b"testdata"
        size = 4
        buf = AsyncBufferedReader(self.AsyncReader(expected), size=size)
        await buf.peek(size)

        actual = await buf.read()
        self.assertEqual(expected, actual)

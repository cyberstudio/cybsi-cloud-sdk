import io
import unittest

from cybsi.cloud.files import LimitedReader, AsyncLimitedReader


class LimitedReaderTest(unittest.TestCase):
    def test_limit_is_equal_to_data_size(self):
        expected = b'test'
        r = LimitedReader(io.BytesIO(expected), limit=len(expected))

        actual = r.read()
        self.assertEqual(expected, actual)

    def test_limit_is_greater_than_data_size(self):
        expected = b'test'
        limit = len(expected) + 1
        r = LimitedReader(io.BytesIO(expected), limit=limit)

        actual = r.read()
        self.assertEqual(expected, actual)

    def test_limit_is_less_than_data_size(self):
        data = b'test'
        limit = len(data) - 1
        expected, expected_rest = data[:limit], data[limit:]
        buf = io.BytesIO(data)
        r = LimitedReader(buf, limit=limit)

        actual = r.read()
        self.assertEqual(expected, actual)

        actual_rest = buf.read()
        self.assertEqual(expected_rest, actual_rest)

    def test_read_size_is_a_multiple_of_limit(self):
        data = b"testdata"
        limit, n = 4, 2
        expected, expected_rest = data[:limit], data[limit:]
        buf = io.BytesIO(data)

        r = LimitedReader(buf, limit=limit)

        actual = b""
        while (chunk := r.read(n)) != b"":
            actual += chunk

        self.assertEqual(expected, actual)
        actual_rest = buf.read()
        self.assertEqual(expected_rest, actual_rest)

    def test_read_size_is_not_a_multiple_of_limit(self):
        data = b"testdata"
        limit, n = 4, 3
        expected, expected_rest = data[:limit], data[limit:]
        buf = io.BytesIO(data)

        r = LimitedReader(buf, limit=limit)

        actual = b""
        while (chunk := r.read(n)) != b"":
            actual += chunk

        self.assertEqual(expected, actual)
        actual_rest = buf.read()
        self.assertEqual(expected_rest, actual_rest)


class AsyncLimitedReaderTest(unittest.IsolatedAsyncioTestCase):
    class AsyncReader:
        def __init__(self, data: bytes):
            self._buf = io.BytesIO(data)

        async def read(self, n: int = -1):
            return self._buf.read(n)

    async def test_limit_is_equal_to_data_size(self):
        expected = b'test'
        r = AsyncLimitedReader(self.AsyncReader(expected), limit=len(expected))

        actual = await r.read()
        self.assertEqual(expected, actual)

    async def test_limit_is_greater_than_data_size(self):
        expected = b'test'
        limit = len(expected) + 1
        r = AsyncLimitedReader(self.AsyncReader(expected), limit=limit)

        actual = await r.read()
        self.assertEqual(expected, actual)

    async def test_limit_is_less_than_data_size(self):
        data = b'test'
        limit = len(data) - 1
        expected, expected_rest = data[:limit], data[limit:]
        buf = self.AsyncReader(data)
        r = AsyncLimitedReader(buf, limit=limit)

        actual = await r.read()
        self.assertEqual(expected, actual)

        actual_rest = await buf.read()
        self.assertEqual(expected_rest, actual_rest)

    async def test_read_size_is_a_multiple_of_limit(self):
        data = b"testdata"
        limit, n = 4, 2
        expected, expected_rest = data[:limit], data[limit:]
        buf = self.AsyncReader(data)

        r = AsyncLimitedReader(buf, limit=limit)

        actual = b""
        while (chunk := await r.read(n)) != b"":
            actual += chunk

        self.assertEqual(expected, actual)
        actual_rest = await buf.read()
        self.assertEqual(expected_rest, actual_rest)

    async def test_read_size_is_not_a_multiple_of_limit(self):
        data = b"testdata"
        limit, n = 4, 3
        expected, expected_rest = data[:limit], data[limit:]
        buf = self.AsyncReader(data)

        r = AsyncLimitedReader(buf, limit=limit)

        actual = b""
        while (chunk := await r.read(n)) != b"":
            actual += chunk

        self.assertEqual(expected, actual)
        actual_rest = await buf.read()
        self.assertEqual(expected_rest, actual_rest)

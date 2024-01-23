import unittest
from typing import Union

import httpx


class BaseTest(unittest.TestCase):
    @staticmethod
    def _make_response(status_code: int, content: Union[list, dict]):
        """Make mock response"""
        return httpx.Response(status_code=status_code, json=content)


class BaseAsyncTest(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    async def _make_async_response(status_code: int, content: Union[list, dict]):
        """Make mock response"""
        return httpx.Response(status_code=status_code, json=content)

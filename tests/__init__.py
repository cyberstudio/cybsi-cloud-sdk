import datetime
import unittest
from typing import Union

import httpx

from cybsi.cloud.internal import parse_rfc3339_timestamp


class BaseTest(unittest.TestCase):
    @staticmethod
    def _make_response(status_code: int, content: Union[list, dict]):
        """Make mock response"""
        return httpx.Response(status_code=status_code, json=content)

    @staticmethod
    def assert_timestamp(expected_timestamp: str, actual_timestamp: datetime.datetime):
        """Assert given timestamp with expected

        expected_timestamp string format is %Y-%m-%dT%H:%M:%S.%fZ
        """
        assert parse_rfc3339_timestamp(expected_timestamp) == actual_timestamp

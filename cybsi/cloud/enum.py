from enum import Enum
from functools import lru_cache
from typing import TypeVar

ET = TypeVar("ET")


class CybsiAPIEnum(Enum):
    """CybsiAPIEnum is a base class for all Cybsi Cloud API enumerations."""

    @classmethod
    @lru_cache()
    def from_string(cls, value: str, ignore_case=False):
        """Convert a string value to enumeration value.

        Args:
            value: value to convert.
            ignore_case: ignore enumeration values case.
        Return:
            Enumeration value.
        """
        try:
            return cls(value)
        except ValueError as exp:
            if not ignore_case:
                raise exp from None

            for member in cls:
                if str(member.value).lower() == value.lower():
                    return member

            raise exp from None

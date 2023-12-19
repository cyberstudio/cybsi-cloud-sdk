from enum_tools import document_enum

from ..enum import CybsiAPIEnum
from ..internal import JsonObjectView


@document_enum
class ObjectKeyType(CybsiAPIEnum):
    """Object key type."""

    MD5Hash = "MD5Hash"
    SHA1Hash = "SHA1Hash"
    SHA256Hash = "SHA256Hash"
    SHA512Hash = "SHA512Hash"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"
    IPNetwork = "IPNetwork"


@document_enum
class ObjectType(CybsiAPIEnum):
    """Object type."""

    File = "File"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"
    IPNetwork = "IPNetwork"


class ObjectKeyView(JsonObjectView):
    """Object key view"""

    @property
    def type(self) -> ObjectKeyType:
        """Object key type"""
        return ObjectKeyType.from_string(self._get("type"))

    @property
    def value(self) -> str:
        """Key value."""
        return self._get("value")

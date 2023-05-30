from ..internal import BaseAPI
from .api_key import APIKeysAPI
from .resource import ResourcesAPI


class AuthAPI(BaseAPI):
    """Auth API."""

    @property
    def api_keys(self) -> APIKeysAPI:
        """API-Keys API handle."""
        return APIKeysAPI(self._connector)

    @property
    def resources(self) -> ResourcesAPI:
        """Resources API handle."""
        return ResourcesAPI(self._connector)

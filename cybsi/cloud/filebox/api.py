from ..internal import BaseAPI, BaseAsyncAPI
from .files import FilesAPI, FilesAsyncAPI


class FileboxAPI(BaseAPI):
    """Filebox API."""

    @property
    def files(self) -> FilesAPI:
        """Filebox files handle."""
        return FilesAPI(self._connector)


class FileboxAsyncAPI(BaseAsyncAPI):
    """Filebox asynchronous API."""

    @property
    def files(self) -> FilesAsyncAPI:
        """Filebox files handle."""
        return FilesAsyncAPI(self._connector)

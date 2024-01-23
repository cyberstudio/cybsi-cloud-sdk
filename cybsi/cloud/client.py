from .auth import APIKeyAuth, AuthAPI
from .client_config import Config
from .files import FilesAPI, FilesAsyncAPI
from .insight.api import InsightAPI, InsightAsyncAPI
from .internal import AsyncHTTPConnector, HTTPConnector
from .iocean import IOCeanAPI, IOCeanAsyncAPI


class Client:
    """The main entry point for all actions with Cybsi Cloud REST API.

    As the client is low-level, it is structured around Cybsi Cloud REST API routes.
    Use properties of the client to retrieve handles of API sections.

    The client also follows Cybsi Cloud REST API input-output formats,
    providing little to no abstration from JSONs API uses.
    It's relatively easy to construct an invalid request,
    so use client's functions wisely.

    Hint:
        Use :class:`~cybsi.cloud.Client` properties
        to construct needed API handles. Don't construct sub-APIs manually.

        Do this:
            >>> from cybsi.cloud import Client
            >>> client = Client(config)
            >>> res = client.iocean.collections.filter()
        Not this:
            >>> from cybsi.cloud.iocean import IOCeanAPI
            >>> IOceanAPI(connector).collections

    Args:
        config: Client config.
    Usage:
        >>> from cybsi.cloud import Config, Client
        >>> api_key = "8Nqjk6V4Q_et_Rf5EPu4SeWy4nKbVPKPzKJESYdRd7E"
        >>> config = Config(api_key)
        >>> client = Client(config)
        >>>
        >>> collections = client.iocean.collections.filter()
        >>> print(collections.data())
        >>> client.close()  # "with" syntax is also supported for Client
    """

    def __init__(self, config: Config):
        auth = APIKeyAuth(api_url=config.api_url, api_key=config.api_key)

        self._connector = HTTPConnector(
            base_url=config.api_url,
            auth=auth,
            ssl_verify=config.ssl_verify,
            timeouts=config.timeouts,
            limits=config.limits,
        )

    def __enter__(self) -> "Client":
        self._connector.__enter__()
        return self

    def __exit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        self._connector.__exit__(exc_type, exc_value, traceback)

    def close(self) -> None:
        """Close client and release connections."""
        self._connector.close()

    @property
    def auth(self) -> AuthAPI:
        """Auth API handle."""
        return AuthAPI(self._connector)

    @property
    def iocean(self) -> IOCeanAPI:
        """IOCean API handle."""
        return IOCeanAPI(self._connector)

    @property
    def insight(self) -> InsightAPI:
        """Insight API handle."""
        return InsightAPI(self._connector)

    @property
    def files(self) -> FilesAPI:
        """Files API handle."""
        return FilesAPI(self._connector)


class AsyncClient:
    """The asynchronous analog of :class:`Client`.

    As you can see, the asynchronous client has fewer features than synchronous one.
    This is because we don't simply copy-paste features,
    but provide them only when they're actually useful in asynchronous applications.

    Args:
        config: Client config.
    """

    def __init__(self, config: Config):
        auth = APIKeyAuth(api_url=config.api_url, api_key=config.api_key)

        self._connector = AsyncHTTPConnector(
            base_url=config.api_url,
            auth=auth,
            ssl_verify=config.ssl_verify,
            timeouts=config.timeouts,
            limits=config.limits,
        )

    async def __aenter__(self) -> "AsyncClient":
        await self._connector.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type=None,
        exc_value=None,
        traceback=None,
    ) -> None:
        await self._connector.__aexit__(exc_type, exc_value, traceback)

    async def aclose(self) -> None:
        """Close client and release connections."""
        await self._connector.aclose()

    @property
    def iocean(self) -> IOCeanAsyncAPI:
        """IOCean asynchronous API handle."""
        return IOCeanAsyncAPI(self._connector)

    @property
    def insight(self) -> InsightAsyncAPI:
        """Insight asynchronous API handle."""
        return InsightAsyncAPI(self._connector)

    @property
    def files(self) -> FilesAsyncAPI:
        """Files API handle."""
        return FilesAsyncAPI(self._connector)

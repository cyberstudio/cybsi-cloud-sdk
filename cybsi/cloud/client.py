from dataclasses import dataclass
from typing import Callable, Union

from .auth import APIKeyAuth, AuthAPI
from .client_config import DEFAULT_LIMITS, DEFAULT_TIMEOUTS, Limits, Timeouts
from .error import CybsiError
from .internal import HTTPConnector
from .iocean import IOCeanAPI


@dataclass
class Config:
    """:class:`Client` config.

    Args:
        api_url: Base API URL.
        auth: Optional callable :class:`Client` can use to authenticate requests.
            In most cases it's enough to pass `api_key` instead of this.
        ssl_verify: Enable SSL certificate verification.
        timeouts: Timeout configuration. Default configuration is 5 sec
            on all operations.
        limits:  Configuration for limits to various client behaviors.
            Default configuration is max_connections=100, max_keepalive_connections=20.
    """

    api_url: str
    auth: Union[APIKeyAuth, Callable]
    ssl_verify: bool = True  # TODO: remove?
    timeouts: Timeouts = DEFAULT_TIMEOUTS
    limits: Limits = DEFAULT_LIMITS


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
            >>> client.iocean.collections
        Not this:
            >>> from cybsi.cloud.iocean import IOCeanAPI
            >>> IOceanAPI(connector).collections

    Args:
        config: Client config.
    Usage:
        >>> from cybsi.cloud import APIKeyAuth, Config, Client
        >>> api_url = "https://cybsi.cloud/"
        >>> api_key = "8Nqjk6V4Q_et_Rf5EPu4SeWy4nKbVPKPzKJESYdRd7E"
        >>> auth = APIKeyAuth(api_url, api_key)
        >>> config = Config(api_url, auth)
        >>> client = Client(config)
        >>>
        >>> client.iocean.collections
        >>> client.close()  # "with" syntax is also supported for Client
    """

    def __init__(self, config: Config):
        if config.auth is None:
            raise CybsiError("No authorization mechanism configured for client")

        self._connector = HTTPConnector(
            base_url=config.api_url,
            auth=config.auth,
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

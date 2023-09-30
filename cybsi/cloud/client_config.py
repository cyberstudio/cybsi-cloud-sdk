from typing import Optional, Union

import httpx

from .api import Null, Nullable, _unwrap_nullable

TimeoutTypes = Union[
    Optional[float],
    "Timeouts",
]


class Limits:
    """Configuration for limits to various client behaviors.

    Args:
        max_connections: The maximum number of concurrent connections that may be
            established.
        max_keepalive_connections: Allow the connection pool to maintain
            keep-alive connections below this point. Should be less than or equal
            to `max_connections`.
        keepalive_expiry: The maximum time (in second) to allow before closing
            a keep-alive connection.
    """

    def __init__(
        self,
        *,
        max_connections: Optional[int] = None,
        max_keepalive_connections: Optional[int] = None,
        keepalive_expiry: Optional[float] = 5.0,
    ):
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry

    def _as_httpx_limits(self) -> httpx.Limits:
        return httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            keepalive_expiry=self.keepalive_expiry,
        )


class Timeouts:
    """Timeout configuration.

    Note:
        Default parameters value is :data:`~cybsi.cloud.Null`,
        it means "use default timeout".
        :data:`None` value means "infinite timeout".

        Please note those timeouts don't restrict total execution time
        of SDK methods (like register, view and so on).
        Wrap calls to SDK methods with asyncio.wait_for or
        similar functions if you want to control total execution time.
    Args:
        default: Timeout (in seconds) on all operations listed below.
        connect: The maximum amount of time (in seconds) to wait
            for a connection attempt to a server to succeed.
        read: The maximum amount of time (in seconds) to wait between
            consecutive read operations for a response from the server.
        write: The maximum amount of time (in seconds) to wait between
            consecutive write operations (send request) to the server.
    Raises:
        :class:`ValueError`: Timeout must either default settings
            for all operations or set all three parameters explicitly.
    Usage:
        >>> # No timeouts.
        >>> Timeouts(default=None)
        >>> # 5s timeout on all operations.
        >>> Timeouts(default=5.0)
        >>> # 5s timeout on connect, no other timeouts.
        >>> Timeouts(default=None, connect=5.0)
        >>> # 10s timeout on connect. 5s timeout elsewhere.
        >>> Timeouts(default=5.0, connect=10.0)
    """

    def __init__(
        self,
        *,
        default: Nullable[TimeoutTypes] = Null,
        connect: Nullable[float] = Null,
        read: Nullable[float] = Null,
        write: Nullable[float] = Null,
    ):
        if isinstance(default, Timeouts):
            # Passed as a single explicit Timeout.
            assert connect is Null
            assert read is Null
            assert write is Null
            self.connect = _unwrap_nullable(default.connect)  # type: Optional[float]
            self.read = _unwrap_nullable(default.read)  # type: Optional[float]
            self.write = _unwrap_nullable(default.write)  # type: Optional[float]

        elif not (connect is Null or read is Null or write is Null):
            self.connect = _unwrap_nullable(connect)
            self.read = _unwrap_nullable(read)
            self.write = _unwrap_nullable(write)
        else:
            if default is Null:
                raise ValueError(
                    "Timeout must either include default settings "
                    "for all operations or set all three parameters explicitly."
                )
            self.connect = (
                _unwrap_nullable(default)
                if connect is Null
                else _unwrap_nullable(connect)
            )
            self.read = (
                _unwrap_nullable(default) if read is Null else _unwrap_nullable(read)
            )
            self.write = (
                _unwrap_nullable(default) if write is Null else _unwrap_nullable(write)
            )

    def _as_httpx_timeouts(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=self.connect,
            read=self.read,
            write=self.write,
            # Timeout (in seconds) on acquiring connection from pool.
            # Internal default httpx.Timeout setting.
            pool=5.0,
        )


DEFAULT_TIMEOUTS = Timeouts(default=60.0)
DEFAULT_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)


class Config:
    """:class:`Client` config.

    Args:
        api_key: Cybsi Cloud API key.
        api_url: Base API URL.
        ssl_verify: Enable SSL certificate verification.
        timeouts: Timeout configuration. Default configuration is 60 sec
            on all operations.
        limits:  Configuration for limits to various client behaviors.
            Default configuration is max_connections=100, max_keepalive_connections=20.
    """

    def __init__(
        self,
        *,
        api_key: str,
        api_url: str = "https://cybsi.cloud",
        ssl_verify: bool = True,
        timeouts: Timeouts = DEFAULT_TIMEOUTS,
        limits: Limits = DEFAULT_LIMITS,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.ssl_verify = ssl_verify
        self.timeouts = timeouts
        self.limits = limits

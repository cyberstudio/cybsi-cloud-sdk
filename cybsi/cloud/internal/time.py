import datetime


def rfc3339_timestamp(dt: datetime.datetime) -> str:
    """
    Generate an :RFC:`3339`-formatted timestamp in UTC time zone from a
    :class:`datetime.datetime`.
    Microseconds are ignored.
    >>> import datetime as dtm
    >>> rfc3339_timestamp(dtm.datetime(2009,1,1,12,59,59,0,dtm.timezone.utc))
    '2009-01-01T12:59:59Z'
    If timestamp is naive, local time zone is used to calculate shift.
    >>> rfc3339_timestamp(dtm.datetime(2009,1,1,12,59,59,0))
    '2009-01-01T06:59:59Z'
    """
    dt = dt.astimezone(datetime.timezone.utc)
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return timestamp


def parse_rfc3339_timestamp(ts: str) -> datetime.datetime:
    if ts.find(".") != -1:
        return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

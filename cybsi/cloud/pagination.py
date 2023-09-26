"""
Pagination API.

See Also:
    See :ref:`pagination-example`
    for complete examples of pagination usage.
"""
from typing import (
    AsyncIterator,
    Callable,
    Coroutine,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
    cast,
)
from urllib.parse import parse_qs, urlparse

import httpx


class Cursor:
    """Page cursor value.

    If :data:`None` cursor value is **passed** to SDK
    (as a parameter to filter-like functions), SDK retrieves the first page.

    Typically, SDK does not **return** cursors as function return values.
    SDK returns :class:`Page`, and
    cursor is a property of the page.

    :data:`None` cursor value of a page means last page.
    """

    pass


# This is a hack to prevent Sphinx autodoc-typehint type inlining.
# If we simply alias Cursor = str, it inlines str everywhere,
# and functions lose descriptive parameter and return value types.
# Additionally, this hack prevents SDK users from creating Cursor instances.
# Users have to call filter()-like methods.
Cursor.__supertype__ = str  # type: ignore

T = TypeVar("T")


class _BasePage(Generic[T]):
    def __init__(self, resp: httpx.Response, view: Callable[..., T]):
        self._resp = resp
        self._view = view

    @property
    def next_link(self) -> str:
        """Next page link."""
        return cast(str, self._resp.links.get("next", {}).get("url"))

    @property
    def cursor(self) -> Optional[Cursor]:
        """Page cursor. The current position in the collection.

        :data:`None` means the page is last one.
        """
        next_url = self._resp.links.get("next", {}).get("url")
        if next_url is None:
            return None
        parsed = urlparse(next_url)
        query = parse_qs(parsed.query)
        cursor = query.get("cursor")
        return cast(Optional[Cursor], cursor[0]) if cursor is not None else None

    def data(self) -> List[T]:
        """Get page data as a list of items."""
        return list(iter(self))

    def __iter__(self) -> Iterator[T]:
        yield from (self._view(x) for x in self._resp.json())


class Page(_BasePage[T]):
    """Page returned by Cybsi Cloud API.
       Should not be constructed manually, use filter-like methods provided by SDK.

    Args:
        api_call: Callable object for getting next page
        resp: Response which represents a start page
        view: View class for page elements
    """

    def __init__(
        self,
        api_call: Callable[..., httpx.Response],
        resp: httpx.Response,
        view: Callable[..., T],
    ):
        super().__init__(resp, view)
        self._api_call = api_call

    def next_page(self) -> "Optional[Page[T]]":
        """Get next page.
        If there is no link to the next page it return None.
        """
        if self.next_link is None:
            return None

        return Page(self._api_call, self._api_call(self.next_link), self._view)


class AsyncPage(_BasePage[T]):
    """Page returned by Cybsi API.
       Should not be constructed manually, use filter-like methods provided by SDK.

    Args:
        api_call: Callable object for getting next page
        resp: Response which represents a start page
        view: View class for page elements
    """

    def __init__(
        self,
        api_call: Callable[..., Coroutine],
        resp: httpx.Response,
        view: Callable[..., T],
    ):
        super().__init__(resp, view)
        self._api_call = api_call

    async def next_page(self) -> "Optional[AsyncPage[T]]":
        """Get next page.
        If there is no link to the next page it return None.
        """
        if self.next_link is None:
            return None
        resp = await self._api_call(self.next_link)
        return AsyncPage(self._api_call, resp, self._view)


def chain_pages(start_page: Page[T]) -> Iterator[T]:
    """Get chain of collection objects."""

    page: Optional[Page[T]] = start_page
    while page:
        yield from page
        page = page.next_page()


async def chain_pages_async(start_page: AsyncPage[T]) -> AsyncIterator[T]:
    """Get chain of collection objects asynchronously."""
    page: Optional[AsyncPage[T]] = start_page
    while page:
        for elem in page:
            yield elem
        page = await page.next_page()

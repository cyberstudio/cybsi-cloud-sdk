"""
Pagination API.

See Also:
    See :ref:`pagination-example`
    for complete examples of pagination usage.
"""
from typing import Callable, Generic, Iterator, List, Optional, TypeVar, cast

import httpx

T = TypeVar("T")


class _BasePage(Generic[T]):
    def __init__(self, resp: httpx.Response, view: Callable[..., T]):
        self._resp = resp
        self._view = view

    @property
    def next_link(self) -> str:
        """Next page link."""
        # TODO: check if it's correct
        return cast(str, self._resp.links.get("next", {}).get("url"))

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


def chain_pages(start_page: Page[T]) -> Iterator[T]:
    """Get chain of collection objects."""

    page: Optional[Page[T]] = start_page
    while page:
        yield from page
        page = page.next_page()

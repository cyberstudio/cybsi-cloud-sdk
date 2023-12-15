from enum_tools import document_enum

from ..enum import CybsiAPIEnum
from ..internal import JsonObjectForm, JsonObjectView
from .permission import ResourceAction
from .resource import ResourceRefView


@document_enum
class LimitPeriod(CybsiAPIEnum):
    """Limit time window."""

    Day = "Day"
    """Time window with period of one day."""


class RequestLimitTargetView(JsonObjectView):
    """Request limit target."""

    @property
    def resource(self) -> ResourceRefView:
        """Resource."""
        return ResourceRefView(self._get("resource"))

    @property
    def action(self) -> ResourceAction:
        """Limited action."""
        return ResourceAction(self._get("action"))


class RequestLimitView(JsonObjectView):
    """Request limit."""

    @property
    def target(self) -> RequestLimitTargetView:
        """Limit target."""
        return RequestLimitTargetView(self._get("target"))

    @property
    def limit(self) -> int:
        """Maximum requests count within time window."""
        return self._get("limit")

    @property
    def period(self) -> LimitPeriod:
        """Time window for limit."""
        return LimitPeriod(self._get("period"))


class RequestLimitForm(JsonObjectForm):
    """Request limit form.

    Args:
        resource_id: resource identifier.
        action: limited action.
        limit_period: time window for limit.
        limit: maximum requests count within time window.
    """

    def __init__(
        self,
        *,
        resource_id: int,
        action: ResourceAction,
        limit_period: LimitPeriod,
        limit: int,
    ):
        super().__init__()
        self._data["target"] = {"resource": {"id": resource_id}, "action": action.value}
        self._data["limit"] = limit
        self._data["period"] = limit_period.value

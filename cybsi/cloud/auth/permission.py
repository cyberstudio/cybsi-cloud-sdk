from typing import Iterable, List

from enum_tools import document_enum

from ..enum import CybsiAPIEnum
from ..internal import JsonObjectForm, JsonObjectView
from .resource import ResourceRefView


@document_enum
class ResourceAction(CybsiAPIEnum):
    """Resource action."""

    Read = "Read"
    """Allows to read the resource."""
    Write = "Write"
    """Allows to modify the resource."""
    ReadChildren = "ReadChildren"
    """Allows to read direct children resources without direct permission."""
    WriteChildren = "WriteChildren"
    """Allows to modify direct children resources without direct permission."""


class ResourcePermissionView(JsonObjectView):
    """Resource permission."""

    @property
    def resource(self) -> ResourceRefView:
        """Resource."""
        return ResourceRefView(self._get("resource"))

    @property
    def actions(self) -> List[ResourceAction]:
        """List of permitted actions."""
        return [ResourceAction(act) for act in self._get("actions")]


class ResourcePermissionForm(JsonObjectForm):
    """Resource permissions form.

    This is the form for resource permissions you have to fill to generate API-Key.

    Args:
        resource_id: resource identifier.
        actions: permitted actions for resource.
    """

    def __init__(
        self,
        *,
        resource_id: int,
        actions: Iterable[ResourceAction],
    ):
        super().__init__()
        self._data["resource"] = {"id": resource_id}
        self._data["actions"] = [act.value for act in actions]

from ..internal import BaseAPI, BaseAsyncAPI
from .schemas import SchemaAPI, SchemaAsyncAPI
from .task_queue import TaskQueueAPI, TaskQueueAsyncAPI
from .tasks import TaskAPI, TaskAsyncAPI


class InsightAPI(BaseAPI):
    """Insight API."""

    @property
    def schemas(self) -> SchemaAPI:
        """Get Insight schemas handle."""
        return SchemaAPI(self._connector)

    @property
    def tasks(self) -> TaskAPI:
        """Get Insight task handle."""
        return TaskAPI(self._connector)

    @property
    def task_queue(self) -> TaskQueueAPI:
        """Get Insight task queue handle."""
        return TaskQueueAPI(self._connector)


class InsightAsyncAPI(BaseAsyncAPI):
    """Insight asynchronous API."""

    @property
    def schemas(self) -> SchemaAsyncAPI:
        """Schemas asynchronous API handle."""
        return SchemaAsyncAPI(self._connector)

    @property
    def tasks(self) -> TaskAsyncAPI:
        """Tasks asynchronous API handle."""
        return TaskAsyncAPI(self._connector)

    @property
    def task_queue(self) -> TaskQueueAsyncAPI:
        """Task queue asynchronous API handle."""
        return TaskQueueAsyncAPI(self._connector)

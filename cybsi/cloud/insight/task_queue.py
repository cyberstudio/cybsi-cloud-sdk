import uuid
from datetime import datetime
from typing import Iterable, List

from ..internal import (
    BaseAPI,
    BaseAsyncAPI,
    JsonObject,
    JsonObjectView,
    parse_rfc3339_timestamp,
)
from .tasks import ObjectKeyForm, ObjectType, TaskParamsView

_PATH = "insight/task-queue"


class TaskQueueAPI(BaseAPI):
    """Task queue API."""

    def pop_tasks(self, *, limit: int) -> List["TaskQueueItemView"]:
        """Take the list of enrichment tasks to execution.

        Note:
            Calls `POST /insight/task-queue/executing-tasks`.
        Args:
            limit: The maximum number of tasks to execution.
        Returns:
            Limited list of task queue item views.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        path = f"{_PATH}/executing-tasks"
        resp = self._connector.do_post(path=path, json={"limit": limit})
        return [TaskQueueItemView(task) for task in resp.json()]

    def complete_task(
        self,
        *,
        task_id: uuid.UUID,
        obj_type: ObjectType,
        keys: Iterable[ObjectKeyForm],
        context: JsonObject = {},
    ) -> None:
        """Register the successful enrichment result.

        Note:
            Calls `POST /insight/task-queue/completed-tasks`.
        Args:
            task_id: Task identifier.
            obj_type: Type of the object.
            keys: Keys of the object.
            context: Additional data describing object.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.TaskNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidState`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaCheckFail`

            Object keys is validated according to the schema specified in the
            :attr:`~cybsi.cloud.insight.tasks.TaskForm`.
        """
        path = f"{_PATH}/completed-tasks"
        payload = {
            "taskID": str(task_id),
            "result": {
                "type": obj_type.value,
                "keys": [key.json() for key in keys],
                "context": context,
            },
        }
        self._connector.do_post(path=path, json=payload)

    def fail_task(self, *, task_id: uuid.UUID, code: str, message: str) -> None:
        """Register the enrichment error.

        Note:
            Calls `POST /insight/task-queue/failed-tasks`.
        Args:
            task_id: Task identifier.
            code: Enrichment error code.
            message: Enrichment error message.
        Note:
            The enrichment error code and message must be specified by external system.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.TaskNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidState`
        """
        path = f"{_PATH}/failed-tasks"
        payload = {"taskID": str(task_id), "error": {"code": code, "message": message}}
        self._connector.do_post(path=path, json=payload)


class TaskQueueAsyncAPI(BaseAsyncAPI):
    """Task queue asynchronous API."""

    async def pop_tasks(self, *, limit: int) -> List["TaskQueueItemView"]:
        """Take the list of enrichment tasks to execution.

        Note:
            Calls `POST /insight/task-queue/executing-tasks`.
        Args:
            limit: The maximum number of tasks to execution.
        Returns:
            Limited list of task queue item views.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
        """
        path = f"{_PATH}/executing-tasks"
        resp = await self._connector.do_post(path=path, json={"limit": limit})
        return [TaskQueueItemView(task) for task in resp.json()]

    async def complete_task(
        self,
        *,
        task_id: uuid.UUID,
        obj_type: ObjectType,
        keys: Iterable[ObjectKeyForm],
        context: JsonObject = {},
    ) -> None:
        """Register the successful enrichment result.

        Note:
            Calls `POST /insight/task-queue/completed-tasks`.
        Args:
            task_id: Task identifier.
            obj_type: Type of the object.
            keys: Keys of the object.
            context: Additional data describing object.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.TaskNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidState`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaCheckFail`

            Object keys is validated according to the schema specified in the
            :attr:`~cybsi.cloud.insight.tasks.TaskForm`.
        """
        path = f"{_PATH}/completed-tasks"
        payload = {
            "taskID": str(task_id),
            "result": {
                "type": obj_type.value,
                "keys": [key.json() for key in keys],
                "context": context,
            },
        }
        await self._connector.do_post(path=path, json=payload)

    async def fail_task(self, *, task_id: uuid.UUID, code: str, message: str) -> None:
        """Register the enrichment error.

        Note:
            Calls `POST /insight/task-queue/failed-tasks`.
        Args:
            task_id: Task identifier.
            code: Enrichment error code.
            message: Enrichment error message.
        Note:
            The enrichment error code and message must be specified by external system.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see args value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Request contains logic errors.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.TaskNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidState`
        """
        path = f"{_PATH}/failed-tasks"
        payload = {"taskID": str(task_id), "error": {"code": code, "message": message}}
        await self._connector.do_post(path=path, json=payload)


class TaskQueueItemView(JsonObjectView):
    """Task queue item view."""

    @property
    def id(self) -> uuid.UUID:
        """Task identifier."""
        return uuid.UUID(self._get("id"))

    @property
    def created_at(self) -> datetime:
        """Task created at"""
        return parse_rfc3339_timestamp(self._get("createdAt"))

    @property
    def params(self) -> TaskParamsView:
        """Task params."""
        return TaskParamsView(self._get("params"))

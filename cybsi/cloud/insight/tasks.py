import uuid
from typing import Iterable, List, Optional, cast

from enum_tools import document_enum

from ..enum import CybsiAPIEnum
from ..internal import BaseAPI, BaseAsyncAPI, JsonObject, JsonObjectForm, JsonObjectView

_PATH = "/insight/tasks"


@document_enum
class ObjectKeyType(CybsiAPIEnum):
    """Object key type."""

    MD5Hash = "MD5Hash"
    SHA1Hash = "SHA1Hash"
    SHA256Hash = "SHA256Hash"
    SHA512Hash = "SHA512Hash"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"


@document_enum
class ObjectType(CybsiAPIEnum):
    """Object type."""

    File = "File"
    DomainName = "DomainName"
    URL = "URL"
    IPAddress = "IPAddress"


@document_enum
class TaskState(CybsiAPIEnum):
    """Object key type."""

    Pending = "Pending"
    """Task awaits execution."""
    Completed = "Completed"
    """Task successfully completed."""
    Failed = "Failed"
    """Task completed with error."""


class TaskAPI(BaseAPI):
    """Task API."""

    def register(self, task: "TaskForm") -> "TaskRegistrationView":
        """Register new enrichment task.

        Note:
            Calls `POST /insight/tasks`.
        Args:
            task: Task registration form.
        Returns:
            Task registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
            :class:`~cybsi.cloud.error.TooManyRequestsError`: Request limit exceeded.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.FileNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
            Too many requests error codes specific for this method:
              * :attr:`~cybsi.cloud.error.TooManyRequestsErrorCodes.LimitExceeded`
        """
        resp = self._connector.do_post(path=_PATH, json=task.json())
        return TaskRegistrationView(resp.json())

    def view(self, task_id: uuid.UUID) -> "TaskView":
        """Get the enrichment task view.

        Note:
            Calls `GET /insight/tasks/{task_id}`.
        Args:
            task_id: Task identifier.
        Returns:
            Task view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Task not found.
        """

        path = f"{_PATH}/{task_id}"
        resp = self._connector.do_get(path=path)
        return TaskView(resp.json())


class TaskAsyncAPI(BaseAsyncAPI):
    """Tasks asynchronous API."""

    async def register(self, task: "TaskForm") -> "TaskRegistrationView":
        """Register new enrichment task.

        Note:
            Calls `POST /insight/tasks`.
        Args:
            task: Task registration form.
        Returns:
            Task registration view.
        Raises:
            :class:`~cybsi.cloud.error.InvalidRequestError`:
                Provided values are invalid (see form value requirements).
            :class:`~cybsi.cloud.error.SemanticError`: Form contains logic errors.
            :class:`~cybsi.cloud.error.TooManyRequestsError`: Request limit exceeded.
        Note:
            Semantic error codes specific for this method:
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.SchemaNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.FileNotFound`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeySet`
              * :attr:`~cybsi.cloud.error.SemanticErrorCodes.InvalidKeyFormat`
            Too many requests error codes specific for this method:
              * :attr:`~cybsi.cloud.error.TooManyRequestsErrorCodes.LimitExceeded`
        """
        resp = await self._connector.do_post(path=_PATH, json=task.json())
        return TaskRegistrationView(resp.json())

    async def view(self, task_id: uuid.UUID) -> "TaskView":
        """Get the enrichment task view.

        Note:
            Calls `GET /insight/tasks/{task_id}`.
        Args:
            task_id: Task identifier.
        Returns:
            Task view.
        Raises:
            :class:`~cybsi.cloud.error.NotFoundError`: Task not found.
        """

        path = f"{_PATH}/{task_id}"
        resp = await self._connector.do_get(path=path)
        return TaskView(resp.json())


class TaskRegistrationView(JsonObjectView):
    """Task registration view"""

    @property
    def id(self) -> uuid.UUID:
        """Task identifier."""
        return uuid.UUID(self._get("taskID"))


class ObjectKeyView(JsonObjectView):
    """Object key view"""

    @property
    def type(self) -> ObjectKeyType:
        """Object key type"""
        return ObjectKeyType.from_string(self._get("type"))

    @property
    def value(self) -> str:
        """Key value."""
        return self._get("value")


class TaskParamsView(JsonObjectView):
    """Task params view."""

    @property
    def schema_id(self) -> str:
        """URL friendly string, uniquely identifies json schema."""
        return self._get("schemaID")

    @property
    def object_keys(self) -> List[ObjectKeyView]:
        """List of object keys."""
        return self._map_list_optional("objectKeys", ObjectKeyView)

    @property
    def file_id(self) -> Optional[str]:
        """File identifier. Use filebox to upload file. See :ref:`filebox`
        for information about filebox.
        """
        return self._get_optional("fileID")


class TaskErrorView(JsonObjectView):
    """Task error view."""

    @property
    def code(self) -> str:
        """Error code."""
        return self._get("code")


class TaskView(JsonObjectView):
    """Task view"""

    @property
    def id(self) -> uuid.UUID:
        """Task identifier."""
        return uuid.UUID(self._get("id"))

    @property
    def params(self) -> TaskParamsView:
        """Task params."""
        return TaskParamsView(self._get("params"))

    @property
    def state(self) -> TaskState:
        """Task state."""
        return TaskState(self._get("state"))

    @property
    def result(self) -> JsonObject:
        """Task result.

        Note:
            This value is present if task state is :attr:`~.TaskState.Completed`
        """
        return cast(JsonObject, self._get("result"))

    @property
    def error(self) -> TaskErrorView:
        """Task error.

        Note:
            This value is present if task state is :attr:`~.TaskState.Failed`
        """
        return TaskErrorView(self._get("result"))


class ObjectKeyForm(JsonObjectForm):
    """Object key form."""

    def __init__(self, key_type: ObjectKeyType, value: str):
        super().__init__()
        self._data["type"] = key_type.value
        self._data["value"] = value


class TaskForm(JsonObjectForm):
    """Task form"""

    def __init__(
        self,
        schema_id: str,
        object_keys: Optional[Iterable[ObjectKeyForm]] = None,
        file_id: Optional[str] = None,
    ):
        super().__init__()
        params: dict = {
            "schemaID": schema_id,
        }
        if object_keys is not None:
            params["objectKeys"] = [key.json() for key in object_keys]
        if file_id is not None:
            params["fileID"] = file_id
        self._data["params"] = params

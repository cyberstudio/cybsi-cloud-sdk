import uuid
from typing import List
from unittest.mock import patch

from cybsi.cloud.internal import HTTPConnector, parse_rfc3339_timestamp, AsyncHTTPConnector

from cybsi.cloud.client_config import DEFAULT_TIMEOUTS, DEFAULT_LIMITS
from cybsi.cloud.insight import TaskQueueAPI, TaskQueueItemView, ObjectKeyView, ObjectType, ObjectKeyForm, \
    ObjectKeyType, TaskQueueAsyncAPI
from tests import BaseTest, BaseAsyncTest


class TaskQueueAPITest(BaseTest):
    def setUp(self) -> None:
        self.base_url = "http://localhost"
        self.connector = HTTPConnector(
            base_url=self.base_url,
            auth=None,
            ssl_verify=True,
            timeouts=DEFAULT_TIMEOUTS,
            limits=DEFAULT_LIMITS,
        )

        self.task_queue_api = TaskQueueAPI(self.connector)

    @patch.object(HTTPConnector, "do_post")
    def test_pop_tasks(self, mock):
        limit = 1
        expected_task_id_str = "e68c61ee-3bad-4eee-909b-8a95e482bcdd"
        expected_created_at_str = "2023-12-07T05:11:03.024Z"
        expected_schema_id = "test-schema"
        expected_object_key_type_str = "DomainName"
        expected_object_key_value = "test.com"

        def side_effect(path, json):
            assert json["limit"] == limit
            content = [
                {
                    "id": expected_task_id_str,
                    "createdAt": expected_created_at_str,
                    "params": {
                        "schemaID": expected_schema_id,
                        "objectKeys": [
                            {
                                "type": expected_object_key_type_str,
                                "value": "test.com",
                            },
                        ],
                    },
                },
            ]
            return self._make_response(200, content)
        mock.side_effect = side_effect

        actual_tasks: List[TaskQueueItemView] = self.task_queue_api.pop_tasks(limit=limit)
        assert len(actual_tasks) == limit
        actual_task = actual_tasks[0]
        assert actual_task.id == uuid.UUID(expected_task_id_str)
        assert actual_task.created_at == parse_rfc3339_timestamp(expected_created_at_str)
        assert actual_task.params.schema_id == expected_schema_id
        actual_object_key: ObjectKeyView = actual_task.params.object_keys[0]
        assert actual_object_key.type.value == expected_object_key_type_str
        assert actual_object_key.value == expected_object_key_value

    @patch.object(HTTPConnector, "do_post")
    def test_complete_task(self, mock):
        expected_task_id = uuid.UUID("e68c61ee-3bad-4eee-909b-8a95e482bcdd")
        expected_object_type = ObjectType.DomainName
        expected_object_key = ObjectKeyForm(key_type=ObjectKeyType.DomainName, value="test.com")

        def side_effect(path, json):
            assert json["taskID"] == str(expected_task_id)
            actual_result = json["result"]
            assert actual_result["type"] == expected_object_type.value
            assert len(actual_result["keys"]) == 1
            actual_object_key = actual_result["keys"][0]
            assert actual_object_key["type"] == expected_object_key.json()["type"]
            assert actual_object_key["value"] == expected_object_key.json()["value"]
            return self._make_response(204, {})
        mock.side_effect = side_effect

        self.task_queue_api.complete_task(
            task_id=expected_task_id,
            obj_type=expected_object_type,
            keys=[expected_object_key],
        )

    @patch.object(HTTPConnector, "do_post")
    def test_fail_task(self, mock):
        expected_task_id = uuid.UUID("e68c61ee-3bad-4eee-909b-8a95e482bcdd")
        expected_code = "ErrTestCode"
        expected_message = "Error test code"

        def side_effect(path, json):
            assert json["taskID"] == str(expected_task_id)
            assert json["error"]["code"] == expected_code
            assert json["error"]["message"] == expected_message
        mock.side_effect = side_effect

        self.task_queue_api.fail_task(task_id=expected_task_id, code=expected_code, message=expected_message)


class TaskQueueAsyncAPITest(BaseAsyncTest):
    def setUp(self) -> None:
        self.base_url = "http://localhost"
        self.connector = AsyncHTTPConnector(
            base_url=self.base_url,
            auth=None,
            ssl_verify=True,
            timeouts=DEFAULT_TIMEOUTS,
            limits=DEFAULT_LIMITS,
        )

        self.task_queue_api = TaskQueueAsyncAPI(self.connector)

    @patch.object(AsyncHTTPConnector, "do_post")
    async def test_pop_tasks(self, mock):
        limit = 1
        expected_task_id_str = "e68c61ee-3bad-4eee-909b-8a95e482bcdd"
        expected_created_at_str = "2023-12-07T05:11:03.024Z"
        expected_schema_id = "test-schema"
        expected_object_key_type_str = "DomainName"
        expected_object_key_value = "test.com"

        async def side_effect(path, json):
            assert json["limit"] == limit
            content = [
                {
                    "id": expected_task_id_str,
                    "createdAt": expected_created_at_str,
                    "params": {
                        "schemaID": expected_schema_id,
                        "objectKeys": [
                            {
                                "type": expected_object_key_type_str,
                                "value": "test.com",
                            },
                        ],
                    },
                },
            ]
            return await self._make_async_response(200, content)
        mock.side_effect = side_effect

        actual_tasks: List[TaskQueueItemView] = await self.task_queue_api.pop_tasks(limit=limit)
        assert len(actual_tasks) == limit
        actual_task = actual_tasks[0]
        assert actual_task.id == uuid.UUID(expected_task_id_str)
        assert actual_task.created_at == parse_rfc3339_timestamp(expected_created_at_str)
        assert actual_task.params.schema_id == expected_schema_id
        actual_object_key: ObjectKeyView = actual_task.params.object_keys[0]
        assert actual_object_key.type.value == expected_object_key_type_str
        assert actual_object_key.value == expected_object_key_value

    @patch.object(AsyncHTTPConnector, "do_post")
    async def test_complete_task(self, mock):
        expected_task_id = uuid.UUID("e68c61ee-3bad-4eee-909b-8a95e482bcdd")
        expected_object_type = ObjectType.DomainName
        expected_object_key = ObjectKeyForm(key_type=ObjectKeyType.DomainName, value="test.com")

        async def side_effect(path, json):
            assert json["taskID"] == str(expected_task_id)
            actual_result = json["result"]
            assert actual_result["type"] == expected_object_type.value
            assert len(actual_result["keys"]) == 1
            actual_object_key = actual_result["keys"][0]
            assert actual_object_key["type"] == expected_object_key.json()["type"]
            assert actual_object_key["value"] == expected_object_key.json()["value"]
            return await self._make_async_response(204, {})
        mock.side_effect = side_effect

        await self.task_queue_api.complete_task(
            task_id=expected_task_id,
            obj_type=expected_object_type,
            keys=[expected_object_key],
        )

    @patch.object(AsyncHTTPConnector, "do_post")
    async def test_fail_task(self, mock):
        expected_task_id = uuid.UUID("e68c61ee-3bad-4eee-909b-8a95e482bcdd")
        expected_code = "ErrTestCode"
        expected_message = "Error test code"

        async def side_effect(path, json):
            assert json["taskID"] == str(expected_task_id)
            assert json["error"]["code"] == expected_code
            assert json["error"]["message"] == expected_message
            return await self._make_async_response(204, {})

        mock.side_effect = side_effect

        await self.task_queue_api.fail_task(task_id=expected_task_id, code=expected_code, message=expected_message)

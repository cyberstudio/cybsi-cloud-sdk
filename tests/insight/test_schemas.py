from typing import List, Any
from unittest.mock import patch

from cybsi.cloud import Tag
from cybsi.cloud.client_config import DEFAULT_TIMEOUTS, DEFAULT_LIMITS
from cybsi.cloud.insight import SchemaAPI
from cybsi.cloud.internal import HTTPConnector
from cybsi.cloud.pagination import chain_pages
from tests import BaseTest


class SchemasTest(BaseTest):
    def setUp(self) -> None:
        self.base_url = "http://localhost"
        self.connector = HTTPConnector(
            base_url=self.base_url,
            auth=None,
            ssl_verify=True,
            timeouts=DEFAULT_TIMEOUTS,
            limits=DEFAULT_LIMITS,
        )
        self.schemas_api = SchemaAPI(self.connector)
        self.schema_id = "test-schema"
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "schemaID": self.schema_id,
            "title": "Schema example",
        }

    @patch.object(HTTPConnector, "do_post")
    def test_schema_api_register(self, mock) -> None:
        expected_response = {"schemaID": self.schema_id}
        mock.return_value = self._make_response(201, expected_response)

        actual_response = self.schemas_api.register(self.schema)
        assert actual_response.raw() == expected_response

    @patch.object(HTTPConnector, "do_put")
    def test_schema_api_update(self, mock) -> None:
        mock.return_value = self._make_response(204, {})

        self.schemas_api.update(schema_id=self.schema_id, schema=self.schema, tag=Tag())

    @patch.object(HTTPConnector, "do_get")
    def test_schema_api_view(self, mock) -> None:
        mock.return_value = self._make_response(200, self.schema)

        actual_schema = self.schemas_api.view(self.schema_id)
        assert actual_schema.raw() == self.schema

    @patch.object(HTTPConnector, "do_get")
    def test_schema_api_filter(self, mock) -> None:
        schemas_response: List[Any] = [
            {
                "schemaID": "test#1",
                "title": "test schema #1",
            },
            {
                "schemaID": "test#1",
                "title": "test schema #2",
            },
            {
                "schemaID": "test#1",
                "title": "test schema #3",
            },
        ]
        mock.return_value = self._make_response(200, schemas_response)

        start_page = self.schemas_api.filter()
        for actualSchema, expectedSchema in zip(chain_pages(start_page), schemas_response):
            assert actualSchema.schema_id == expectedSchema["schemaID"]
            assert actualSchema.title == expectedSchema["title"]

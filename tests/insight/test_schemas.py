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

    @patch.object(HTTPConnector, "do_post")
    def test_schema_api_register(self, mock) -> None:
        schemaID = "test-schema"
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "schemaID": schemaID,
            "title": "Пример схемы",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Возможные типы объектов",
                    "enum": [
                        "File"
                    ]
                },
                "keys": {
                    "type": "array",
                    "description": "Возможные ключи",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "type": {
                                "type": "string"
                            },
                            "value": {
                                "type": "string"
                            }
                        }
                    }
                },
                "context": {
                    "type": "object",
                    "description": "Контекст объекта",
                    "additionalProperties": False,
                    "required": [
                        "size",
                        "names",
                        "exploitedVulnerabilities"
                    ],
                    "properties": {
                        "size": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Размер файла в байтах"
                        },
                        "names": {
                            "type": "array",
                            "description": "Возможные имена файла",
                            "items": {
                                "type": "string"
                            }
                        },
                        "exploitedVulnerabilities": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "Идентификаторы используемых уязвимостей",
                                "example": "CVE-2023-4321"
                            }
                        }
                    }
                }
            }
        }
        expected_response = {
            "schemaID": schemaID
        }

        mock.return_value = self._make_response(201, expected_response)

        actual_response = self.schemas_api.register(schema)
        assert actual_response.raw() == expected_response

    @patch.object(HTTPConnector, "do_put")
    def test_schema_api_update(self, mock) -> None:
        schemaID = "test-schema"
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "schemaID": schemaID,
            "title": "Пример схемы",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Возможные типы объектов",
                    "enum": [
                        "File"
                    ]
                },
                "keys": {
                    "type": "array",
                    "description": "Возможные ключи",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "type": {
                                "type": "string"
                            },
                            "value": {
                                "type": "string"
                            }
                        }
                    }
                },
                "context": {
                    "type": "object",
                    "description": "Контекст объекта",
                    "additionalProperties": False,
                    "required": [
                        "size",
                        "names",
                        "exploitedVulnerabilities"
                    ],
                    "properties": {
                        "size": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Размер файла в байтах"
                        },
                        "names": {
                            "type": "array",
                            "description": "Возможные имена файла",
                            "items": {
                                "type": "string"
                            }
                        },
                        "exploitedVulnerabilities": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "Идентификаторы используемых уязвимостей",
                                "example": "CVE-2023-4321"
                            }
                        }
                    }
                }
            }
        }

        mock.return_value = self._make_response(204, {})

        self.schemas_api.update(schema_id=schemaID, schema=schema, tag=Tag())

    @patch.object(HTTPConnector, "do_get")
    def test_schema_api_view(self, mock) -> None:
        expected_schema_id = "test-schema"
        expected_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "schemaID": expected_schema_id,
            "title": "Пример схемы",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Возможные типы объектов",
                    "enum": [
                        "File"
                    ]
                },
                "keys": {
                    "type": "array",
                    "description": "Возможные ключи",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "type": {
                                "type": "string"
                            },
                            "value": {
                                "type": "string"
                            }
                        }
                    }
                },
                "context": {
                    "type": "object",
                    "description": "Контекст объекта",
                    "additionalProperties": False,
                    "required": [
                        "size",
                        "names",
                        "exploitedVulnerabilities"
                    ],
                    "properties": {
                        "size": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Размер файла в байтах"
                        },
                        "names": {
                            "type": "array",
                            "description": "Возможные имена файла",
                            "items": {
                                "type": "string"
                            }
                        },
                        "exploitedVulnerabilities": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "Идентификаторы используемых уязвимостей",
                                "example": "CVE-2023-4321"
                            }
                        }
                    }
                }
            }
        }

        mock.return_value = self._make_response(200, expected_schema)

        actual_schema = self.schemas_api.view(expected_schema_id)
        assert actual_schema.raw() == expected_schema

    @patch.object(HTTPConnector, "do_get")
    def test_schema_api_filter(self, mock) -> None:
        schemas_response: List[Any] = [
            {
                "schemaID": "test#1",
                "title": "test schema #1"
            },
            {
                "schemaID": "test#1",
                "title": "test schema #2"
            },
            {
                "schemaID": "test#1",
                "title": "test schema #3"
            }
        ]

        mock.return_value = self._make_response(200, schemas_response)

        start_page = self.schemas_api.filter()
        for actualSchema, expectedSchema in zip(chain_pages(start_page), schemas_response):
            assert actualSchema.schema_id == expectedSchema["schemaID"]
            assert actualSchema.title == expectedSchema["title"]

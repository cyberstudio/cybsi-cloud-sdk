#!/usr/bin/env python3
import json
import os

from cybsi.cloud import APIKeyAuth, Client, Config
from cybsi.cloud.error import ConflictError

if __name__ == "__main__":
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")
    auth = APIKeyAuth(api_url=api_url, api_key=api_key)
    config = Config(api_url, auth)
    client = Client(config)

    jsonSchema = """
    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "schemaID": "example-schema",
      "title": "Пример схемы",
      "description": "string",
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "description": "Возможные типы объектов",
          "enum": [
            "File"
          ]
        },
        "context": {
          "type": "object",
          "description": "Контекст объекта",
          "additionalProperties": false,
          "required": [
            "size"
          ],
          "properties": {
            "size": {
              "type": "integer",
              "minimum": 0,
              "description": "Размер файла в байтах"
            }
          }
        }
      }
    }"""

    schema_id = None
    schema = json.loads(jsonSchema)
    try:  # register object schema
        sch_ref = client.iocean.schemas.register(schema)
        schema_id = sch_ref.schema_id
    except ConflictError:
        # handle Duplicate Error here
        exit(1)

    view = client.iocean.schemas.view(schema_id)
    print(view.schema)

    client.close()

.. _data_model:

Cloud data model
================

.. _object_schemas:

Object schemas
--------------

Object schema defines attribute composition of the objects and data types of the attributes.
It's described in JSON Schema format.

This part of the documentation describes rules to create IOCean object schemas.

Example for the object:

.. code-block:: JSON

    {
        "type": "File",
        "keys": [{"type":"MD5Hash", "value": "627fcdb6cc9a5e16d657ca6cdef0a6bb"}],
        "context": {
            "size": 1024
        },
    }

Required JSON Schema:

.. code-block:: JSON

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
        "keys": {
            "type": "array",
            "description": "Ключи объекта",
            "items": {
                "type": "object",
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
    }

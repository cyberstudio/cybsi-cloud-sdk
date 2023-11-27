.. _data_model:

Cloud Data Model
================

.. _object_schemas:

Object schemas
--------------

Object schema defines attribute composition of the objects and data types of the attributes.
It's described in JSON Schema format.

An object like this:

.. code-block:: JSON

    {
        "type": "File",
        "keys": [{"type":"MD5Hash", "value": "627fcdb6cc9a5e16d657ca6cdef0a6bb"}],
        "context": {
            "size": 1024
        },
    }

Uses JSON Schema:

.. code-block:: JSON

    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "schemaID": "example-schema",
      "title": "Schema example",
      "description": "string",
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "description": "Allowed object types",
          "enum": [
            "File"
          ]
        },
        "keys": {
            "type": "array",
            "description": "Object keys",
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
          "description": "Object context",
          "additionalProperties": false,
          "required": [
            "size"
          ],
          "properties": {
            "size": {
              "type": "integer",
              "minimum": 0,
              "description": "File size (bytes)"
            }
          }
        }
      }
    }

Different collections in Cybsi Cloud usually have different schemas.
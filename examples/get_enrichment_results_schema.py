#!/usr/bin/env python3
from cybsi.cloud import Client, Config

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        schema_id = "example-schema"

        # Retrieve schema. It describes all attributes of objects you can encounter
        # in the result object of the enrichment task with this schema.
        schema_view = client.insight.schemas.view(schema_id="example-schema")

        # Do something with the schema as SchemaView.
        print(schema_view)

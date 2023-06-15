#!/usr/bin/env python3
import os

from cybsi.cloud import Client, Config
from cybsi.cloud.error import (
    ConflictError,
    SchemaCheckErrorDetails,
    SemanticError,
    SemanticErrorCodes,
)
from cybsi.cloud.iocean.objects import ObjectKeyType, ObjectType

if __name__ == "__main__":
    api_url = os.environ.get("CLOUD_BASE_URL", "https://cybsi.cloud")
    api_key = os.environ.get("CLOUD_API_KEY", "api_key")
    config = Config(api_url, api_key)
    client = Client(config)

    collection_id = "example-collection"
    keys = [(ObjectKeyType.MD5Hash, "cea239ce075fcb2151ce9ee10227f042")]
    context = {"size": 112}
    try:  # add collection object
        client.iocean.objects.add(
            collection_id=collection_id,
            obj_type=ObjectType.File,
            keys=keys,
            context=context,
        )
    except ConflictError:
        # handle Duplicate Error here
        exit(1)
    except SemanticError as ex:
        if ex.code == SemanticErrorCodes.SchemaCheckFail:
            details = SchemaCheckErrorDetails(ex.content.details)
            print(details.absolute_keyword_location)
            print(details.instance_location)
            print(details.message)
        exit(1)

    client.close()

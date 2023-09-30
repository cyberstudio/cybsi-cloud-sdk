#!/usr/bin/env python3
from datetime import datetime, timedelta

from cybsi.cloud import Client, Config
from cybsi.cloud.auth import APIKeyForm, ResourceAction, ResourcePermissionForm

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        permissions = [
            ResourcePermissionForm(resource_id=1, actions=[ResourceAction.Read])
        ]
        expires_at = datetime.now() + timedelta(hours=9)
        new_key = APIKeyForm(
            permissions, expires_at=expires_at, description="new test key"
        )
        key_ref = client.auth.api_keys.generate(new_key)
        # do something with the key
        # do not forget to save key_ref.key. It is not recoverable if lost.

#!/usr/bin/env python3
from cybsi.cloud import Client, Config
from cybsi.cloud.insight import ObjectKeyForm, TaskForm
from cybsi.cloud.insight.tasks import ObjectKeyType

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        schema_id = "phishing"

        # define task params
        keys = [ObjectKeyForm(ObjectKeyType.DomainName, "example.com")]
        task_form = TaskForm(schema_id, keys)
        # create task
        task = client.insight.tasks.register(task_form)
        # store task identifier
        print(task.id)

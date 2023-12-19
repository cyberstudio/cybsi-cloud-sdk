#!/usr/bin/env python3

import uuid

from cybsi.cloud import Client, Config
from cybsi.cloud.insight import TaskState

if __name__ == "__main__":
    config = Config(api_key="the cryptic string")

    with Client(config) as client:
        # task identifier
        task_id = uuid.UUID("d3bcba79-2a0f-41ec-a3da-52e82eea4b2b")
        # get task view
        task = client.insight.tasks.view(task_id)
        if task.state == TaskState.Completed:
            # handle result
            print(task.result)
        elif task.state == TaskState.Failed:
            # handle task error
            print(task.error)
        else:
            # retry after some time
            pass

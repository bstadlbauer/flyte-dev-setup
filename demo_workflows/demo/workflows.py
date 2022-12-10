import time

from flytekit import task, workflow, Resources
from flytekitplugins.dask.task import Dask


@task(task_config=Dask())
def demo_task(seconds_to_sleep: int):
    print(f"Will sleep {seconds_to_sleep} seconds now", flush=True)
    time.sleep(seconds_to_sleep)


@workflow
def demo_workflow(seconds_to_sleep: int):
    demo_task(seconds_to_sleep=seconds_to_sleep)

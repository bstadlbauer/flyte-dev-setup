import time

from flytekit import task, workflow, Resources
from flytekitplugins.dask.task import Dask, DaskCluster, JobPodSpec

from dask.distributed import Client


@task(
    task_config=Dask(
        cluster=DaskCluster(
            n_workers=1,
            # requests=Resources(cpu="2", mem="500Mi"),
        ),
        job_pod_spec=JobPodSpec(
            # requests=Resources(cpu="2", mem="1Gi"),
            # limits=Resources(cpu="2", mem="1Gi"),
        ),
    ),
    limits=Resources(cpu="2", mem="500Mi"),
)
def demo_task(seconds_to_sleep: int):
    client = Client()
    print(client, flush=True)

    print(f"Will sleep {seconds_to_sleep} seconds now", flush=True)
    time.sleep(seconds_to_sleep)


@workflow
def demo_workflow(seconds_to_sleep: int):
    demo_task(seconds_to_sleep=seconds_to_sleep)

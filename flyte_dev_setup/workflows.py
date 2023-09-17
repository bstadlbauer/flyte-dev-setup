import os

from distributed import Client
from flytekit import task, workflow, Resources, PodTemplate
from flytekit.core.pod_template import PRIMARY_CONTAINER_DEFAULT_NAME
from flytekitplugins.dask import Dask, Scheduler
from kubernetes.client import V1PodSpec, V1Container


def _get_dask_client_on_runner() -> Client:
    dask_scheduler_address = os.environ["DASK_SCHEDULER_ADDRESS"]
    client = Client(dask_scheduler_address)
    client.wait_for_workers(1)
    return client


@task(
    task_config=Dask(),
    # Limit resources to be able to run on a local cluster
    limits=Resources(cpu="0.5", mem="500Mi"),
)
def simple_dask_dask():
    _get_dask_client_on_runner()


@task(
    task_config=Dask(),
    # Limit resources to be able to run on a local cluster
    limits=Resources(cpu="0.5", mem="500Mi"),
    pod_template=PodTemplate(
        pod_spec=V1PodSpec(
            containers=[
                V1Container(
                    name=PRIMARY_CONTAINER_DEFAULT_NAME,
                    env=[
                        {
                            "name": "NODE_NAME",
                            "valueFrom": {
                                "fieldRef": {
                                    "fieldPath": "spec.nodeName",
                                },
                            },
                        },
                    ],
                ),
            ],
        ),
    ),
)
def pod_template_dask_task():
    def check_node_name_is_set():
        node_name = os.environ.get("NODE_NAME")
        if node_name is None:
            raise ValueError("NODE_NAME environment variable is not set")

    check_node_name_is_set()

    client = _get_dask_client_on_runner()
    client.run_on_scheduler(check_node_name_is_set)
    client.run(check_node_name_is_set)


@workflow
def dask_test_workflow():
    # All tasks are run sequentially to make sure enough resources are available on the
    # local k8s cluster
    simple = simple_dask_dask()

    pod_template = pod_template_dask_task()
    simple >> pod_template

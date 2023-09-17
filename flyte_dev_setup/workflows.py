import os
import time

from distributed import Client
from flytekit import (
    task,
    workflow,
    Resources,
    PodTemplate,
    LaunchPlan,
    Labels,
    Annotations,
)
from flytekit.core.pod_template import PRIMARY_CONTAINER_DEFAULT_NAME
from flytekitplugins.dask import Dask, Scheduler, WorkerGroup
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
def simple_dask_task():
    _get_dask_client_on_runner()


@task(
    task_config=Dask(
        workers=WorkerGroup(
            number_of_workers=2,
        )
    ),
    # Limit resources to be able to run on a local cluster
    limits=Resources(cpu="0.5", mem="500Mi"),
)
def two_workers_task():
    client = _get_dask_client_on_runner()
    client.wait_for_workers(2)


@task(
    task_config=Dask(),
    # Limit resources to be able to run on a local cluster
    limits=Resources(cpu="0.5", mem="500Mi"),
    environment={"FOO": "BAR"},
)
def environment_variables_set_task():
    def check_foo_is_set():
        foo = os.environ.get("FOO")
        if foo is None or foo != "BAR":
            raise ValueError("FOO environment variable is not set")

    check_foo_is_set()

    client = _get_dask_client_on_runner()
    client.run_on_scheduler(check_foo_is_set)
    client.run(check_foo_is_set)


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
                            "name": "TEST_LABEL",
                            "valueFrom": {
                                "fieldRef": {
                                    "fieldPath": "metadata.labels['test']",
                                },
                            },
                        },
                    ],
                ),
            ],
        ),
    ),
)
def labels_task():
    def check_if_label_is_set():
        label = os.environ.get("TEST_LABEL")
        if label is None or label != "test-label":
            raise ValueError("TEST_LABEL environment variable is not set")

    check_if_label_is_set()

    client = _get_dask_client_on_runner()
    client.run_on_scheduler(check_if_label_is_set)
    client.run(check_if_label_is_set)


@workflow
def labels_workflow():
    labels_task()


labels_launch_plan = LaunchPlan.get_or_create(
    labels_workflow,
    "labels_launch_plan",
    labels=Labels({"test": "test-label"}),
)


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
                            "name": "TEST_ANNOTATION",
                            "valueFrom": {
                                "fieldRef": {
                                    "fieldPath": "metadata.annotations['test']",
                                },
                            },
                        },
                    ],
                ),
            ],
        ),
    ),
)
def annotations_task():
    def check_if_annotations_is_set():
        annotation = os.environ.get("TEST_ANNOTATION")
        if annotation is None or annotation != "test-annotation":
            raise ValueError("TEST_ANNOTATION environment variable is not set")

    check_if_annotations_is_set()

    client = _get_dask_client_on_runner()
    client.run_on_scheduler(check_if_annotations_is_set)
    client.run(check_if_annotations_is_set)


@workflow
def annotation_workflow():
    annotations_task()


annotations_launch_plan = LaunchPlan.get_or_create(
    annotation_workflow,
    "annotation_launch_plan",
    annotations=Annotations({"test": "test-annotation"}),
)


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
    simple = simple_dask_task()

    two_workers = two_workers_task()
    simple >> two_workers

    environment = environment_variables_set_task()
    two_workers >> environment

    # Passing on labels does currently not work
    # labels = labels_launch_plan()
    # environment >> labels

    annotations = annotations_launch_plan()
    environment >> annotations

    pod_template = pod_template_dask_task()
    annotations >> pod_template

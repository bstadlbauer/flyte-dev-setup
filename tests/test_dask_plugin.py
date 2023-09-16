"""End-to-end tests for the Dask plugin."""
import pytest
from flytekit.remote import FlyteWorkflow, FlyteRemote

from flyte_dev_setup.workflows import do_nothing_workflow


@pytest.fixture
def demo_workflow(
    flyte_version: str, flyte_remote: FlyteRemote, register_workflows: None
) -> FlyteWorkflow:
    workflow_name = f"{do_nothing_workflow.__module__}.{do_nothing_workflow.__name__}"
    workflow = flyte_remote.fetch_workflow(name=workflow_name, version=flyte_version)
    return workflow


def test_dask_cluster(demo_workflow: FlyteWorkflow, flyte_remote: FlyteRemote):
    execution = flyte_remote.execute_remote_wf(
        demo_workflow,
        inputs={},
        wait=True,
    )
    assert execution is not None
    assert execution.error is None

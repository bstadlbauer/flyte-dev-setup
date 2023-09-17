"""End-to-end tests for the Dask plugin."""
import pytest
from flytekit import WorkflowExecutionPhase
from flytekit.remote import FlyteWorkflow, FlyteRemote

from flyte_dev_setup.workflows import dask_test_workflow


@pytest.fixture
def dask_workflow_fixture(
    flyte_version: str, flyte_remote: FlyteRemote, register_workflows: None
) -> FlyteWorkflow:
    workflow_name = f"{dask_test_workflow.__module__}.{dask_test_workflow.__name__}"
    workflow = flyte_remote.fetch_workflow(name=workflow_name, version=flyte_version)
    return workflow


def test_dask_cluster(dask_workflow_fixture: FlyteWorkflow, flyte_remote: FlyteRemote):
    execution = flyte_remote.execute_remote_wf(
        dask_workflow_fixture,
        inputs={},
        wait=True,
    )
    assert execution is not None
    assert execution.error is None
    assert execution.closure.phase == WorkflowExecutionPhase.SUCCEEDED

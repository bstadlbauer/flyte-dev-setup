# Flyte dev setup

Repo used to easily and automatially end-to-end test the 
[dask integration](https://docs.flyte.org/projects/cookbook/en/stable/auto_examples/k8s_dask_plugin/index.html)
for Flyte.

## Requirements
- [poetry](https://python-poetry.org/)
- [make](https://www.gnu.org/software/make/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [helm](https://helm.sh/)
- [flytectl](https://docs.flyte.org/projects/flytectl/en/latest/)

## Usage
First, make sure to stand up a Flyte dev sandbox k8s cluster which has both all 
Flyte dependencies as well as the 
[dask-k8s-operator](https://kubernetes.dask.org/en/latest/operator.html) running. You 
can do so using 
```shell
make setup
```

During that you'll be asked to start Flyte locally, for more info checkout [the 
development setup guide](https://docs.flyte.org/en/latest/community/contribute.html#development-environment-setup-guide).

To create the python virtual environment, you can run

```shell
poetry install
```

To run all tests, use

```shell
poetry run pytest
```

The tests will: 
1. Build a dockerimage based on `docker/Dockerfile`
2. Register that image to `localhost:30000`
3. Trigger a test workflow from `flyte_dev_setup/workflows.py`. This workflow is 
   designed to test different facets of the plugin and will use the docker image 
   mentioned above.


To check on the status of the workflow, you can check the Flyte UI at http://localhost:30080/console/projects/dask-testing/domains/development/workflows/flyte_dev_setup.workflows.dask_test_workflow


## Versions
Versions of different components are specified in the following places:
- `flytekit`: `./pyproject.toml`
- `flytekitplugins-dask`: `./pyproject.toml`
- `dask`: `./pyproject.toml`
- `dask-kubernetes`: `./pyproject.toml`
- `dask-kubernetes-operator`: `./Makefile` -> Will currently always use the latest (and perform a `helm repo update`)
- `flyte`: Whatever is started locally. Dependencies such as the ingress, docker registry will be whatever is used by `flytectl demo start --dev`.
FLYTE_ADMIN_URL = "dns:///localhost"


DASK_HELM_REPO = dask/dask-kubernetes-operator

# Only required for local dask deployment
#DASK_HELM_REPO = "${HOME}/workspace/bstadlbauer/dask-kubernetes/dask_kubernetes/operator/deployment/helm/dask-kubernetes-operator/"
#DASK_DOCKERFILE = "${HOME}/workspace/bstadlbauer/dask-kubernetes/dask_kubernetes/operator/deployment/Dockerfile"
#DASK_DOCKER_BUILD_CONTEXT = "${HOME}/workspace/bstadlbauer/dask-kubernetes/"

WORKFLOW_DOCKERFILE_BUILD_CONTEXT = "${HOME}/workspace/bstadlbauer/flytekit/plugins/flytekit-dask"

WORKFLOW_VERSION = $(shell date +%F-%H-%M-%S)
# Assign version to make sure it does not change again
WORKFLOW_VERSION := ${WORKFLOW_VERSION}
WORKFLOW_DOCKER_IMAGE = dask-plugin-dev:${WORKFLOW_VERSION}

.PHONY: update-helm-repos
update-helm-repos:
	helm repo update

.PHONY: helm-upgrade-flyte
helm-upgrade-flyte: update-helm-repos
	helm upgrade --install -n flyte --create-namespace flyte -f deployment/flyte/values.yaml flyte/flyte --wait

.PHONY: add-dask-helm-repo
add-dask-helm-repo:
	helm repo add dask https://helm.dask.org

# Only required for local dask deployment
#.PHONY: build-local-dask-image
#build-local-dask-image:
#	docker build -t dask-operator-local:latest -f ${DASK_DOCKERFILE} ${DASK_DOCKER_BUILD_CONTEXT}

.PHONY: helm-upgrade-dask-operator
helm-upgrade-dask-operator: add-dask-helm-repo update-helm-repos# build-local-dask-image # Only required for local dask deployment
	# Removing everything to make sure CRDs are correct
	helm uninstall -n dask dask || true
	kubectl delete crd daskclusters.kubernetes.dask.org || true
	kubectl delete crd daskjobs.kubernetes.dask.org || true
	kubectl delete crd daskworkergroups.kubernetes.dask.org || true
	kubectl delete crd daskautoscalers.kubernetes.dask.org || true
	# helm install -n dask --create-namespace dask -f deployment/dask/values.yaml ${DASK_HELM_REPO} --wait  # Only required for local dask deployment
	helm install -n dask --create-namespace dask ${DASK_HELM_REPO} --wait

.PHONY: create-flyte-project
create-flyte-project:
	cd /Users/bstadlbauer/go/src/github.com/flyteorg/flytectl \
	&& ./bin/flytectl create project --id dask-plugin --name "Dask plugin" --description "Project for dask plugin development" || true

.PHONY: initial-setup
initial-setup: helm-upgrade-flyte helm-upgrade-dask-operator create-flyte-project

.PHONY: build
build:
	docker build -t ${WORKFLOW_DOCKER_IMAGE} -f ./Dockerfile ${WORKFLOW_DOCKERFILE_BUILD_CONTEXT}

.PHONY: run
run: build
	docker run -it --rm ${WORKFLOW_DOCKER_IMAGE} /bin/bash

.PHONY: serialize
serialize: build
	rm -rf ./workflows
	mkdir workflows
	docker run \
		--rm \
		-v /Users/bstadlbauer/workspace/bstadlbauer/flyte-dev-setup/demo_workflows/:/src/demo \
		-v /Users/bstadlbauer/workspace/bstadlbauer/flyte-dev-setup/workflows:/src/workflows \
		--workdir /src \
	    ${WORKFLOW_DOCKER_IMAGE} \
	    pyflyte --pkgs demo package --fast --image ${WORKFLOW_DOCKER_IMAGE} -o /src/workflows/flyte-package.tgz
	tar zxvf ./workflows/flyte-package.tgz -C ./workflows/
	rm ./workflows/flyte-package.tgz

# FIXME: This is super strange! Will only work in the flytectl directory
.PHONY: register
register: serialize
	cd /Users/bstadlbauer/go/src/github.com/flyteorg/flytectl \
	&& ./bin/flytectl -p dask-plugin -d development register files --version ${WORKFLOW_VERSION} /Users/bstadlbauer/workspace/bstadlbauer/flyte-dev-setup/workflows/*

.PHONY: setup
setup: initial-setup build register

export FLYTECTL_CONFIG=/Users/bstadlbauer/.flyte/config-sandbox.yaml

FLYTE_PROJECT = "dask-testing"

.PHONY: test-helm
test-helm:
	@which helm > /dev/null || { echo '\033[0;31mCould not find the 'helm' binary. Please make sure that it is installed.\033[0m'; exit 1; }

.PHONY: test-kubectl
test-kubectl:
	@which kubectl > /dev/null || { echo '\033[0;31mCould not find the 'kubectl' binary. Please make sure that it is installed.\033[0m'; exit 1; }

.PHONY: test-flytectl
test-flytectl:
	@which kubectl > /dev/null || { echo '\033[0;31mCould not find the 'kubectl' binary. Please make sure that it is installed.\033[0m'; exit 1; }

.PHONY: start-flyte-dev-cluster
start-flyte-dev-cluster: test-flytectl
	flytectl demo start --dev

.PHONY: add-dask-helm-repo
add-dask-helm-repo:
	helm repo add dask https://helm.dask.org

.PHONY: update-helm-repos
update-helm-repos:
	helm repo update

.PHONY: deploy-dask-operator
deploy-dask-operator: add-dask-helm-repo update-helm-repos
	helm install --create-namespace -n dask-operator dask-operator dask/dask-kubernetes-operator --wait

.PHONY: check-flyte-is-up
check-flyte-is-up:
	@if ! wget -q --spider http://localhost:30080; then \
		read -p "It seems like Flyte is not up yet, please make sure that you start the single binary and press Enter once done" -n 1 -r; \
	fi

.PHONY: create-dask-project
create-dask-project: test-flytectl check-flyte-is-up
	flytectl create project --id ${FLYTE_PROJECT} --name dask-e2e --description "Dask E2E" || true

.PHONY: create-dask-namespace
create-dask-namespace:
	kubectl create namespace ${FLYTE_PROJECT}-development || true

.PHONY: setup
setup: start-flyte-dev-cluster deploy-dask-operator create-dask-project create-dask-namespace

.PHONY: teardown
teardown: test-flytectl
	flytectl demo teardown

.PHONY: build
build:
	docker build -t ${FLYTE_PROJECT}:dev -f docker/Dockerfile .

.PHONY: run
run: build
	docker run -it --rm --entrypoint /bin/bash ${FLYTE_PROJECT}:dev

.PHONY: push
push: build
	docker tag ${FLYTE_PROJECT}:dev localhost:30000/${FLYTE_PROJECT}:dev
	docker push localhost:30000/${FLYTE_PROJECT}:dev

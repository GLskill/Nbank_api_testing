DOCKER_USER ?=
DOCKER_PASSWORD ?=
IMAGE_NAME = $(DOCKER_USER)/python-test
TAG = latest

DOCKER_COMPOSE_FILE = infra/docker_compose/docker-compose.yml

EST_OUTPUT_DIR ?= test-results/$(shell date +"%Y_%m_%d_%H_%M")
SERVER ?= http://localhost:4111/api
UI_BASE_URL ?= http://localhost:3000

# DOCKER IMAGE
.PHONY: build-docker-container
build-docker-container:
	@echo "going to build docker container with tests"
	docker buildx create --use
	docker buildx build --platform linux/amd64,linux/arm64 -t $(IMAGE_NAME):$(TAG) .

.PHONY: run-docker-container
run-docker-container:
	@echo "going to run docker container with tests"
	mkdir -p $(TEST_OUTPUT_DIR)
	docker run --rm --name test-runner \
		   --platform linux/amd64 \
		   --network host \
		   -v $(shell pwd)/$(TEST_OUTPUT_DIR)/allure-results:/app/allure-results \
		   -e SERVER=$(SERVER) -e UI_BASE_URL=$(UI_BASE_URL) \
           $(IMAGE_NAME):$(TAG)
	@echo "tests finished, check results in $(TEST_OUTPUT_DIR)"

.PHONY: publish-docker-container
publish-docker-container:
	echo $(DOCKER_PASSWORD) | docker login -u $(DOCKER_USER) --password-stdin
	docker buildx build --push --platform linux/amd64,linux/arm64 -t $(IMAGE_NAME):$(TAG) .

# DOCKER COMPOSE
.PHONY: stop-app
stop-app:
	docker compose -f $(DOCKER_COMPOSE_FILE) down

.PHONY: start-app
start-app:
	make stop-app
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d

# RUN TESTS
.PHONY: run-tests
run-tests:
	pytest -v --log-level=DEBUG --log-cli-level=DEBUG --alluredir allure-results

# K8S
.PHONY: k8s-start
k8s-start:
	minikube start --driver=docker
	helm upgrade --install nbank infra/kube/chart

.PHONY: k8s-check-context
k8s-check-context:
	kubectl config current-context

.PHONY: k8s-check-services
k8s-check-services:
	kubectl get svc
	kubectl get pods

.PHONY: k8s-check-logs
k8s-check-logs:
	 kubectl logs deployment/backend

.PHONY: k8s-port-forward
k8s-port-forward:
	 kubectl port-forward svc/frontend 3000:80

.PHONY: k8s-start-monitoring
k8s-start-monitoring:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
	helm repo add grafana https://grafana.github.io/helm-charts || true
	helm repo update
	helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace -f infra/kube/monitoring-values.yaml
	helm upgrade --install loki grafana/loki-stack -n monitoring -f infra/kube/loki-values.yaml
	kubectl create secret generic basic-backend-auth --from-literal=username=admin --from-literal=password=admin -n monitoring
	kubectl apply -f infra/kube/spring-monitoring.yaml

.PHONY: k8s-stop
k8s-stop:
	kubectl delete -f infra/kube/spring-monitoring.yaml || true
	kubectl delete secret basic-backend-auth -n monitoring || true
	helm uninstall monitoring -n monitoring || true
	kubectl delete namespace monitoring || true
	helm uninstall nbank || true
	minikube stop
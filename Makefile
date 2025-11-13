# === Переменные ===
DOCKER_USER ?=
DOCKER_PASSWORD ?=
IMAGE_NAME = $(DOCKER_USER)/python-test
TAG = latest

DOCKER_COMPOSE_FILE = docker-compose-full.yml

# Папка для результатов (с датой)
TEST_OUTPUT_DIR ?= $(shell pwd)/test-results/$(shell date +"%Y-%m-%d_%H-%M-%S")

# Профиль тестов (по умолчанию api)
TEST_PROFILE ?= api

# === DOCKER COMPOSE - ОСНОВНОЙ СПОСОБ ЗАПУСКА ===

.PHONY: test-all
test-all:
	@echo "Running all tests in Docker Compose..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up --build --abort-on-container-exit tests

.PHONY: test-api
test-api:
	@echo "Running API tests..."
	TEST_PROFILE=api docker compose -f $(DOCKER_COMPOSE_FILE) up --build --abort-on-container-exit tests

.PHONY: test-ui
test-ui:
	@echo "Running UI tests..."
	TEST_PROFILE=ui docker compose -f $(DOCKER_COMPOSE_FILE) up --build --abort-on-container-exit tests

.PHONY: start-services
start-services:
	@echo "Starting backend and frontend..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d backend frontend

.PHONY: stop-all
stop-all:
	@echo "Stopping all services..."
	docker compose -f $(DOCKER_COMPOSE_FILE) down

.PHONY: logs-backend
logs-backend:
	docker compose -f $(DOCKER_COMPOSE_FILE) logs -f backend

.PHONY: logs-frontend
logs-frontend:
	docker compose -f $(DOCKER_COMPOSE_FILE) logs -f frontend

.PHONY: logs-tests
logs-tests:
	docker compose -f $(DOCKER_COMPOSE_FILE) logs -f tests

# === ДЛЯ ЗАПУСКА С ВНЕШНИМ BACKEND/FRONTEND ===

.PHONY: test-external-services
test-external-services:
	@echo "Running tests against external services..."
	@echo "Backend: http://localhost:4111"
	@echo "Frontend: http://localhost:3000"
	docker run --rm --name test-runner \
		--network host \
		-v $(shell pwd)/test_results:/app/test_results \
		-v $(shell pwd)/logs:/app/logs \
		-e TEST_PROFILE=$(TEST_PROFILE) \
		-e BASE_API_URL=http://localhost:4111/api \
		-e BASE_UI_URL=http://localhost:3000 \
		python-tests:latest

# === LOCAL TESTING (без Docker) ===

.PHONY: run-tests-local
run-tests-local:
	@echo "Running tests locally..."
	mkdir -p allure-results
	export BASE_API_URL=http://localhost:4111/api && \
	export BASE_UI_URL=http://localhost:3000 && \
	pytest src/tests/$(TEST_PROFILE) -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--html=html_report.html \
		--self-contained-html \
		--junitxml=junit.xml \
		--alluredir=allure-results

# === DOCKER IMAGE ===

.PHONY: build-image
build-image:
	@echo "Building Docker image..."
	docker build -t python-tests:latest .

.PHONY: build-multiplatform
build-multiplatform:
	@echo "Building multi-platform Docker image..."
	docker buildx create --use --name mybuilder || true
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(TAG) \
		--load \
		.

.PHONY: publish-image
publish-image:
	@echo "Logging in and pushing image..."
	echo $(DOCKER_PASSWORD) | docker login -u $(DOCKER_USER) --password-stdin
	docker buildx build --push \
		--platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(TAG) \
		.

# === ALLURE REPORTS ===

.PHONY: allure-serve
allure-serve:
	@echo "Starting Allure report server..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d allure
	@echo "Allure reports available at http://localhost:5050"

.PHONY: allure-stop
allure-stop:
	docker compose -f $(DOCKER_COMPOSE_FILE) stop allure

# === UTILS ===

.PHONY: clean
clean:
	@echo "Cleaning up test results..."
	rm -rf test_results/ test-results/
	rm -f html_report.html junit.xml
	rm -rf allure-results/
	rm -rf logs/

.PHONY: open-report
open-report:
	@echo "Opening latest HTML report..."
	@xdg-open test_results/html_reports/report.html 2>/dev/null || \
	 open test_results/html_reports/report.html 2>/dev/null || \
	 start test_results/html_reports/report.html 2>/dev/null || \
	 echo "Could not open report automatically"

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make test-all              - Run all tests in Docker"
	@echo "  make test-api              - Run API tests only"
	@echo "  make test-ui               - Run UI tests only"
	@echo "  make start-services        - Start backend and frontend"
	@echo "  make stop-all              - Stop all Docker services"
	@echo "  make test-external-services - Test against running localhost services"
	@echo "  make run-tests-local       - Run tests locally (no Docker)"
	@echo "  make allure-serve          - Start Allure report server"
	@echo "  make clean                 - Clean test results"
	@echo "  make build-image           - Build Docker test image"
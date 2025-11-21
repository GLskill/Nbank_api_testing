# === Переменные ===
DOCKER_USER ?=
DOCKER_PASSWORD ?=
IMAGE_NAME = $(DOCKER_USER)/python-test
TAG = latest

# Путь к docker-compose файлу
DOCKER_COMPOSE_FILE = infra/docker_compose/docker-compose.yml

# Профиль тестов (по умолчанию api)
TEST_PROFILE ?= api

# URL для тестов (можно переопределить через env)
BASE_API_URL ?= http://localhost:4111
BASE_UI_URL ?= http://localhost:3000

# === ДЛЯ GITHUB ACTIONS ===

.PHONY: start-app
start-app:
	@echo "Starting backend, frontend and nginx for CI..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d backend frontend nginx
	@echo "Waiting for services to be ready..."
	sleep 20
	@echo "Services started successfully"

.PHONY: run-tests
run-tests:
	@echo "Running tests with:"
	@echo "  BASE_API_URL = $(BASE_API_URL)"
	@echo "  BASE_UI_URL = $(BASE_UI_URL)"
	mkdir -p allure-results
	pytest src/tests/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results

.PHONY: stop-app
stop-app:
	@echo "Stopping services..."
	docker compose -f $(DOCKER_COMPOSE_FILE) down

# === ЛОКАЛЬНЫЙ ЗАПУСК (БЕЗ NGINX, ПОРТ 3000) ===

.PHONY: start-services-local
start-services-local:
	@echo "Starting backend and frontend (without nginx)..."
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d backend frontend
	@echo "Services started on:"
	@echo "  Backend:  http://localhost:4111"
	@echo "  Frontend: http://localhost:3000"

.PHONY: run-tests-local
run-tests-local: start-services-local
	@echo "Waiting for services..."
	@sleep 10
	@echo "Running tests locally (port 3000)..."
	mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 \
	BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results
	@$(MAKE) stop-app

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

.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Local testing (PyCharm):"
	@echo "  make run-tests-local       - Start services on port 3000 and run tests"
	@echo "  make start-services-local  - Start only backend + frontend (port 3000)"
	@echo ""
	@echo "GitHub Actions (CI):"
	@echo "  make start-app             - Start services with nginx (port 80)"
	@echo "  make run-tests             - Run tests (uses BASE_UI_URL from env)"
	@echo "  make stop-app              - Stop all services"
	@echo ""
	@echo "Docker Compose:"
	@echo "  make test-all              - Run all tests in Docker"
	@echo "  make test-api              - Run API tests only"
	@echo "  make test-ui               - Run UI tests only"
	@echo "  make start-services        - Start backend and frontend"
	@echo "  make stop-all              - Stop all services"
	@echo ""
	@echo "Other:"
	@echo "  make allure-serve          - Start Allure report server"
	@echo "  make clean                 - Clean test results"
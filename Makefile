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
	@sleep 20
	@echo "Services started successfully"
	@echo "  Backend:  http://localhost:4111"
	@echo "  Frontend: http://localhost:80 (via nginx)"

.PHONY: run-tests
run-tests:
	@echo "Running tests with:"
	@echo "  BASE_API_URL = $(BASE_API_URL)"
	@echo "  BASE_UI_URL = $(BASE_UI_URL)"
	@mkdir -p allure-results
	BASE_API_URL=$(BASE_API_URL) BASE_UI_URL=$(BASE_UI_URL) \
	pytest src/tests/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results

.PHONY: stop-app
stop-app:
	@echo "Stopping services..."
	docker compose -f $(DOCKER_COMPOSE_FILE) down
	@echo "Services stopped"

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
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results
	@$(MAKE) stop-app

# === БЫСТРЫЙ ЗАПУСК БЕЗ DOCKER (для разработки) ===

.PHONY: test-local-quick
test-local-quick:
	@echo "Running tests (assumes services are already running)..."
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results

.PHONY: test-api-only
test-api-only:
	@echo "Running API tests only..."
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/api/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results

.PHONY: test-ui-only
test-ui-only:
	@echo "Running UI tests only..."
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/ui/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--junitxml=junit.xml \
		--alluredir=allure-results

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

.PHONY: allure-generate
allure-generate:
	@echo "Generating Allure report..."
	allure generate allure-results --clean -o allure-report
	@echo "Report generated in allure-report/"

.PHONY: allure-open
allure-open:
	@echo "Opening Allure report..."
	allure open allure-report

# === UTILS ===

.PHONY: check-services
check-services:
	@echo "Checking services availability..."
	@echo -n "Backend (API): "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:4111/api/health || echo "FAIL"
	@echo -n "Frontend (direct): "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "FAIL"
	@echo -n "Frontend (nginx): "
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:80 || echo "FAIL"

.PHONY: clean
clean:
	@echo "Cleaning up test results..."
	rm -rf test_results/ test-results/
	rm -f html_report.html junit.xml
	rm -rf allure-results/
	rm -rf allure-report/
	rm -rf logs/
	rm -rf .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "=== Разработка (PyCharm) ==="
	@echo "  make start-services-local  - Запустить backend + frontend (порт 3000)"
	@echo "  make test-local-quick      - Запустить тесты (сервисы уже работают)"
	@echo "  make test-api-only         - Только API тесты"
	@echo "  make test-ui-only          - Только UI тесты"
	@echo "  make run-tests-local       - Запустить сервисы + тесты + остановить"
	@echo ""
	@echo "=== GitHub Actions (CI) ==="
	@echo "  make start-app             - Запустить сервисы для CI"
	@echo "  make run-tests             - Запустить тесты (использует BASE_UI_URL)"
	@echo "  make stop-app              - Остановить все сервисы"
	@echo ""
	@echo "=== Docker Compose ==="
	@echo "  make test-all              - Запустить все тесты в Docker"
	@echo "  make test-api              - Только API тесты"
	@echo "  make test-ui               - Только UI тесты"
	@echo "  make start-services        - Запустить backend и frontend"
	@echo "  make stop-all              - Остановить все сервисы"
	@echo ""
	@echo "=== Allure Reports ==="
	@echo "  make allure-generate       - Сгенерировать Allure отчёт"
	@echo "  make allure-open           - Открыть Allure отчёт в браузере"
	@echo "  make allure-serve          - Запустить Allure server (Docker)"
	@echo ""
	@echo "=== Другое ==="
	@echo "  make clean                 - Очистить результаты тестов"
	@echo "  make logs-backend          - Логи backend"
	@echo "  make logs-frontend         - Логи frontend"
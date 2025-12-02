DOCKER_COMPOSE_FILE = infra/docker_compose/docker-compose.yml
BASE_API_URL ?= http://localhost:4111
BASE_UI_URL ?= http://localhost:3000

# GitHub Actions
.PHONY: start-app
start-app:
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d backend frontend nginx
	@sleep 20

.PHONY: run-tests
run-tests:
	@mkdir -p allure-results
	BASE_API_URL=$(BASE_API_URL) BASE_UI_URL=$(BASE_UI_URL) \
	pytest src/tests/ -v --alluredir=allure-results

.PHONY: stop-app
stop-app:
	docker compose -f $(DOCKER_COMPOSE_FILE) down

# Local development
.PHONY: test-local-quick
test-local-quick:
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/ -v --alluredir=allure-results

.PHONY: test-api-only
test-api-only:
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/api/ -v --alluredir=allure-results

.PHONY: test-ui-only
test-ui-only:
	@mkdir -p allure-results
	BASE_API_URL=http://localhost:4111 BASE_UI_URL=http://localhost:3000 \
	pytest src/tests/ui/ -v --alluredir=allure-results

# Services
.PHONY: start-services
start-services:
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d backend frontend

.PHONY: stop-all
stop-all:
	docker compose -f $(DOCKER_COMPOSE_FILE) down

# Cleanup
.PHONY: clean
clean:
	rm -rf allure-results/ allure-report/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

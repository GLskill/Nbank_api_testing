# === Переменные ===
DOCKER_USER ?=
DOCKER_PASSWORD ?=
IMAGE_NAME = $(DOCKER_USER)/python-test
TAG = latest

DOCKER_COMPOSE_FILE = infra/docker-compose/docker-compose.yml

# Папка для результатов (с датой)
TEST_OUTPUT_DIR ?= $(shell pwd)/test-results/$(shell date +"%Y-%m-%d_%H-%M-%S")
SERVER ?= http://localhost:4111/api
UI_BASE_URL ?= http://localhost:3000

# Профиль тестов (по умолчанию api)
TEST_PROFILE ?= api

# === DOCKER IMAGE ===
.PHONY: build-docker-container
build-docker-container:
	@echo "Building multi-platform Docker image..."
	docker buildx create --use --name mybuilder || true
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(TAG) \
		--build-arg TEST_PROFILE=$(TEST_PROFILE) \
		--build-arg BASE_API_URL=$(SERVER) \
		--build-arg BASE_UI_URL=$(UI_BASE_URL) \
		.

.PHONY: run-docker-container
run-docker-container:
	@echo "Running tests in Docker container..."
	@echo "Results will be saved to: $(TEST_OUTPUT_DIR)"
	
	# Создаём папки
	mkdir -p $(TEST_OUTPUT_DIR)/html_reports
	mkdir -p $(TEST_OUTPUT_DIR)/allure_results
	mkdir -p $(TEST_OUTPUT_DIR)/screenshots
	mkdir -p $(TEST_OUTPUT_DIR)/logs

	# Запускаем контейнер
	docker run --rm --name test-runner \
		--platform linux/amd64 \
		--network host \
		-v $(TEST_OUTPUT_DIR)/html_reports:/app/test_results/html_reports \
		-v $(TEST_OUTPUT_DIR)/allure_results:/app/test_results/allure_results \
		-v $(TEST_OUTPUT_DIR)/screenshots:/app/test_results/screenshots \
		-v $(TEST_OUTPUT_DIR)/logs:/app/logs \
		-e TEST_PROFILE=$(TEST_PROFILE) \
		-e BASE_API_URL=$(SERVER) \
		-e BASE_UI_URL=$(UI_BASE_URL) \
		$(IMAGE_NAME):$(TAG)

	@echo "Tests completed. Check results in $(TEST_OUTPUT_DIR)"

.PHONY: publish-docker-container
publish-docker-container:
	@echo "Logging in and pushing image..."
	echo $(DOCKER_PASSWORD) | docker login -u $(DOCKER_USER) --password-stdin
	docker buildx build --push \
		--platform linux/amd64,linux/arm64 \
		-t $(IMAGE_NAME):$(TAG) \
		--build-arg TEST_PROFILE=$(TEST_PROFILE) \
		--build-arg BASE_API_URL=$(SERVER) \
		--build-arg BASE_UI_URL=$(UI_BASE_URL) \
		.

# === DOCKER COMPOSE ===
.PHONY: stop-app
stop-app:
	@echo "Stopping application..."
	docker compose -f $(DOCKER_COMPOSE_FILE) down

.PHONY: start-app
start-app:
	@echo "Starting application..."
	make stop-app
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d

# === LOCAL TESTING ===
.PHONY: run-tests
run-tests:
	@echo "Running tests locally..."
	mkdir -p allure-results
	pytest src/tests/ -v \
		--log-level=DEBUG \
		--log-cli-level=DEBUG \
		--html=html_report.html \
		--self-contained-html \
		--junitxml=junit.xml \
		--alluredir=allure-results

# === UTILS ===
.PHONY: clean
clean:
	@echo "Cleaning up test results..."
	rm -rf test-results/
	rm -f html_report.html junit.xml
	rm -rf allure-results/

.PHONY: logs
logs:
	@echo "Last run log:"
	@cat $(shell ls -t test-results/*/logs/run.log | head -1) 2>/dev/null || echo "No log found"

.PHONY: open-report
open-report:
	@echo "Opening latest HTML report..."
	@open $(shell ls -t test-results/*/html_reports/report.html | head -1) 2>/dev/null || echo "No report found"
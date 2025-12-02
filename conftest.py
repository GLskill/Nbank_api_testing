import os
import pytest
import logging
import requests
from time import sleep

# Импорты фикстур
from src.main.api.fixtures.user_fixtures import *
from src.main.api.fixtures.api_fixtures import *
from src.main.api.fixtures.object_fixtures import *
from src.main.api.fixtures.deposit_fixtures import *
from src.main.api.fixtures.transfer_fixtures import *
from src.main.ui.fixtures.ui_browser_close_fixtures import *
from src.main.ui.fixtures.base_steps_fixtures import *


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Настройка окружения для тестов.
    Поддерживает оба формата переменных:
    - SERVER + API_VERSION (для API)
    - UI_BASE_URL (для UI)
    - BASE_API_URL + BASE_UI_URL (альтернативный формат)
    """
    # API конфигурация
    server = os.getenv("SERVER", "http://localhost:4111/api")
    api_version = os.getenv("API_VERSION", "/v1")
    base_api_url = os.getenv("BASE_API_URL", "http://localhost:4111")

    # UI конфигурация - UI_BASE_URL имеет приоритет
    ui_base_url = os.getenv("UI_BASE_URL")
    base_ui_url = os.getenv("BASE_UI_URL")

    # Определяем финальный UI URL
    final_ui_url = ui_base_url or base_ui_url or "http://localhost:3000"

    # Устанавливаем все варианты для совместимости
    os.environ["SERVER"] = server
    os.environ["API_VERSION"] = api_version
    os.environ["UI_BASE_URL"] = final_ui_url
    os.environ["BASE_API_URL"] = base_api_url
    os.environ["BASE_UI_URL"] = final_ui_url

    print(f"\n{'=' * 60}")
    print(f"Test Environment Configuration:")
    print(f"  SERVER:        {server}")
    print(f"  API_VERSION:   {api_version}")
    print(f"  Full API URL:  {server}{api_version}")
    print(f"  UI_BASE_URL:   {final_ui_url}")
    print(f"  BASE_API_URL:  {base_api_url}")
    print(f"  BASE_UI_URL:   {final_ui_url}")
    print(f"{'=' * 60}\n")

    yield


@pytest.fixture(scope="session", autouse=True)
def healthcheck(setup_test_environment):
    """
    Проверка доступности backend перед запуском тестов.
    Зависит от setup_test_environment чтобы переменные были установлены.
    """
    server = os.getenv("SERVER", "http://localhost:4111/api")

    # Формируем URL для healthcheck
    if server.endswith('/api'):
        health_url = f"{server}/health"
    else:
        health_url = f"{server}/api/health"

    logging.info(f"Backend healthcheck: {health_url}")

    for attempt in range(1, 11):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                logging.info(f"✓ Backend is ready at {health_url}")
                return
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt}/10 failed: {e}")
        sleep(2)

    logging.error(f"❌ Backend health check failed after 10 attempts: {health_url}")
    # Не падаем здесь, пусть тесты попробуют выполниться
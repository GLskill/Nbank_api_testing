import os
import pytest
from src.main.api.fixtures.user_fixtures import *
from src.main.api.fixtures.api_fixtures import *
from src.main.api.fixtures.object_fixtures import *
from src.main.api.fixtures.deposit_fixtures import *
from src.main.api.fixtures.transfer_fixtures import *
from src.main.ui.fixtures.ui_browser_close_fixtures import *
from src.main.ui.fixtures.base_steps_fixtures import *


# Настройка URL из переменных окружения
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Значения по умолчанию для локальной разработки
    default_api_url = "http://localhost:4111"
    default_ui_url = "http://localhost:3000"

    # Получаем из окружения или используем defaults
    base_api_url = os.getenv("BASE_API_URL", default_api_url)
    base_ui_url = os.getenv("BASE_UI_URL", default_ui_url)

    # Устанавливаем переменные для использования в тестах
    os.environ["BASE_API_URL"] = base_api_url
    os.environ["BASE_UI_URL"] = base_ui_url

    print(f"\n{'=' * 60}")
    print(f"Test Environment Configuration:")
    print(f"  API URL: {base_api_url}")
    print(f"  UI URL:  {base_ui_url}")
    print(f"{'=' * 60}\n")

    yield

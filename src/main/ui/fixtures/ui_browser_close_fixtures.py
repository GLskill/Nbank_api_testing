import json
import os
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

from src.main.ui.page_object.user_deposit_money_page import UserDepositMoneyPage
from src.main.ui.page_object.admin_panel_page import AdminPanel
from src.main.ui.page_object.login_page import LoginPage
from src.main.ui.page_object.user_page import UserPage


@pytest.fixture(scope="session")
def config():
    """Загружает конфигурацию с учётом переменных окружения"""

    # Ищем config.json
    config_paths = [
        Path("resources/config.json"),
        Path(__file__).parents[3] / "resources" / "config.json",
    ]

    # Значения по умолчанию
    default_config = {
        "browser": "chromium",
        "headless": True,
        "frontend_url": "http://localhost:3000",
        "backend_url": "http://localhost:4111/api/v1",
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "src/tests/ui/videos/"
    }

    # Загружаем из файла если существует
    config_file = None
    for path in config_paths:
        if path.exists():
            config_file = path
            break

    if config_file:
        with open(config_file, "r", encoding="utf-8") as f:
            file_config = json.load(f)
            default_config.update(file_config)

    # Переопределяем из переменных окружения (приоритет!)
    if os.environ.get('BASE_UI_URL'):
        default_config['frontend_url'] = os.environ.get('BASE_UI_URL')

    if os.environ.get('BASE_API_URL'):
        backend_url = os.environ.get('BASE_API_URL')
        # Добавляем /api/v1 если его нет
        if not backend_url.endswith('/api/v1') and not backend_url.endswith('/api'):
            backend_url = backend_url + '/api/v1'
        default_config['backend_url'] = backend_url

    print(f"\n{'=' * 50}")
    print(f"UI TEST CONFIGURATION")
    print(f"{'=' * 50}")
    print(f"Frontend URL: {default_config['frontend_url']}")
    print(f"Backend URL:  {default_config['backend_url']}")
    print(f"Browser:      {default_config['browser']}")
    print(f"Headless:     {default_config['headless']}")
    print(f"{'=' * 50}\n")

    return default_config


@pytest.fixture(scope="session")
def playwright_instance():
    """Создаёт Playwright instance на всю сессию"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope='function')
def browser_context(config, playwright_instance):
    """Создаёт browser context для каждого теста"""
    browser_type = getattr(playwright_instance, config["browser"])
    browser = browser_type.launch(headless=config["headless"])
    context = browser.new_context(
        viewport=config["viewport"],
        record_video_dir=config["record_video_dir"] if not config["headless"] else None
    )
    page = context.new_page()
    page.set_default_timeout(5000)

    yield page

    context.close()
    browser.close()


@pytest.fixture(scope='function')
def page_objects(browser_context, config):
    """Создаёт все Page Objects для тестов"""
    return {
        "login": LoginPage(browser_context, config["frontend_url"]),
        "admin": AdminPanel(browser_context, config["frontend_url"]),
        "dashboard": UserPage(browser_context, config["frontend_url"]),
        "deposit": UserDepositMoneyPage(browser_context, config["frontend_url"])
    }
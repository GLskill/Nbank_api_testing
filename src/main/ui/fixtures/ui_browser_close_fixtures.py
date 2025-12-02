import os
import pytest
from playwright.sync_api import sync_playwright

from src.main.ui.page_object.user_deposit_money_page import UserDepositMoneyPage
from src.main.ui.page_object.admin_panel_page import AdminPanel
from src.main.ui.page_object.login_page import LoginPage
from src.main.ui.page_object.user_page import UserPage


@pytest.fixture(scope="session")
def config():
    """
    Конфигурация для UI тестов.
    Приоритет: переменные окружения > config.json defaults
    """
    # Читаем из переменных окружения с fallback
    ui_base_url = os.getenv("UI_BASE_URL") or os.getenv("BASE_UI_URL", "http://localhost:3000")

    browser = os.getenv("BROWSER", "chromium")
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    return {
        "browser": browser,
        "headless": headless,
        "frontend_url": ui_base_url,  # ✅ Теперь из переменных окружения
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "src/tests/ui/videos/"
    }


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope='function')
def browser_context(config, playwright_instance):
    browser_type = getattr(playwright_instance, config["browser"])
    browser = browser_type.launch(headless=config["headless"])
    context = browser.new_context(
        viewport=config["viewport"],
        record_video_dir=config["record_video_dir"]
    )
    page = context.new_page()
    # Увеличиваем timeout для GitHub Actions
    page.set_default_timeout(30000)  # ✅ Увеличено с 5000 до 30000
    yield page
    context.close()
    browser.close()


@pytest.fixture(scope='function')
def page_objects(browser_context, config):
    """
    Фикстура для Page Objects.
    Автоматически использует frontend_url из config (который берёт из ENV)
    """
    frontend_url = config["frontend_url"]

    print(f"[DEBUG] Creating page objects with frontend_url: {frontend_url}")

    return {
        "login": LoginPage(browser_context, frontend_url),
        "admin": AdminPanel(browser_context, frontend_url),
        "dashboard": UserPage(browser_context, frontend_url),
        "deposit": UserDepositMoneyPage(browser_context, frontend_url)
    }
import logging
from time import sleep
import pytest
import requests
from config import Config


# === 1. Healthcheck бэкенда ===
@pytest.fixture(scope="session", autouse=True)
def healthcheck():
    logging.info("Waiting for backend to become available...")
    url = Config.SERVER.rstrip("/")
    for i in range(30):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code < 500:  # 200, 401, 404 — всё ок
                logging.info(f"Backend is ready! ({r.status_code})")
                return
        except requests.exceptions.RequestException:
            pass
        logging.info(f"Waiting for backend... ({i + 1}/30)")
        sleep(3)
    raise RuntimeError("Backend failed to start!")


# === 2. Playwright фикстуры (обязательно!) ===
pytest_plugins = [
    "pytest_playwright.pytest_playwright",  # ← это включает browser, context, page
]


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": Config.UI_BASE_URL,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture()
def page_objects(page):
    from src.main.ui.page_objects import LoginPage, DashboardPage, CreateUserPage
    return {
        "login": LoginPage(page),
        "dashboard": DashboardPage(page),
        "create_user": CreateUserPage(page),
    }


# === 3. Фикстуры для deposit и transfer (если у тебя они есть в проекте) ===
# Если их нет — просто создай заглушки, которые делают то же самое, что и раньше

@pytest.fixture()
def deposit_setup(api_manager):
    # Пример: создаём двух пользователей и аккаунты
    user1 = api_manager.create_user()
    user2 = api_manager.create_user()
    acc1 = api_manager.create_account(user1["id"])
    acc2 = api_manager.create_account(user2["id"])
    return {"from_account": acc1, "to_account": acc2, "users": [user1, user2]}


@pytest.fixture()
def transfer_setup(api_manager):
    # То же самое
    return deposit_setup(api_manager)  # или свой код
import json

import pytest
from playwright.sync_api import sync_playwright

from src.main.ui.page_object.user_deposit_money_page import UserDepositMoneyPage
from src.main.ui.page_object.admin_panel_page import AdminPanel
from src.main.ui.page_object.login_page import LoginPage
from src.main.ui.page_object.user_page import UserPage


@pytest.fixture(scope="session")
def config():
    with open("resources/config.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope='function')  # Before_ALL
def browser_context(config, playwright_instance):
    browser_type = getattr(playwright_instance, config["browser"])
    browser = browser_type.launch(headless=config["headless"])
    context = browser.new_context(viewport=config["viewport"], record_video_dir=config["record_video_dir"])
    page = context.new_page()
    page.set_default_timeout(5000)
    yield page
    context.close()
    browser.close()


@pytest.fixture(scope='function')
def page_objects(browser_context, config):
    return {
        "login": LoginPage(browser_context, config["frontend_url"]),
        "admin": AdminPanel(browser_context, config["frontend_url"]),
        "dashboard": UserPage(browser_context, config["frontend_url"]),
        "deposit": UserDepositMoneyPage(browser_context, config["frontend_url"])
    }

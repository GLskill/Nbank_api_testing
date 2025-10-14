import os

import allure
from playwright.sync_api import sync_playwright

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps

os.makedirs("screenshots", exist_ok=True)
os.makedirs("videos", exist_ok=True)


@allure.title("admin login with correct data test")
@allure.description("Test admin successful login to the system by the UI")
def test_admin_can_login_with_correct_data():
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    base_url = "http://localhost:3000"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir="videos/")
        page = context.new_page()

        page.goto(f"{base_url}")
        page.get_by_placeholder("Username").fill(admin.username)
        page.get_by_placeholder("Password").fill(admin.password)
        page.locator("button").click()
        page.get_by_text("Admin Panel").wait_for(state="visible")

        screenshot_path = "screenshots/admin_login_result.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Login Screenshot", attachment_type=allure.attachment_type.PNG)

        context.close()
        browser.close()


@allure.title("user login with correct data test")
@allure.description("Test user successful login to the system by the UI")
def test_user_can_login_with_correct_data():
    admin_steps = AdminSteps([])
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    user = admin_steps.create_user(user_request)
    base_url = "http://localhost:3000"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir="videos/")
        page = context.new_page()

        page.goto(f"{base_url}")
        page.get_by_placeholder("Username").fill(user_request.username)
        page.get_by_placeholder("Password").fill(user_request.password)
        page.locator("button").click()
        page.get_by_text("User Dashboard").wait_for(state="visible")

        screenshot_path = "screenshots/user_login_result.png"
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name="Login Screenshot", attachment_type=allure.attachment_type.PNG)

        context.close()
        browser.close()

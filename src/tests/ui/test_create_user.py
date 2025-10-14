import os

import allure
from playwright.sync_api import sync_playwright, Dialog

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps

os.makedirs("screenshots", exist_ok=True)
os.makedirs("videos", exist_ok=True)


@allure.title("admin login with correct data test")
@allure.description("Test admin successful login to the system by the UI")
def test_admin_can_login_with_correct_data():
    admin_steps = AdminSteps([])
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    base_url = "http://localhost:3000"
    new_user = RandomModelGenerator.generate(CreateUserRequest)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir="videos/")
        page = context.new_page()

        page.goto(base_url)  # 1 step login admin
        page.get_by_placeholder("Username").fill(admin.username)
        page.get_by_placeholder("Password").fill(admin.password)
        page.locator("button").click()
        page.get_by_text("Admin Panel").wait_for(state="visible")

        page.get_by_placeholder("Username").fill(new_user.username)  # 2 step  create user
        page.get_by_placeholder("Password").fill(new_user.password)

        with page.expect_event("dialog") as dialog_info:  # Check alert
            page.get_by_role("button", name="Add User").click()

        dialog: Dialog = dialog_info.value
        alert_text = dialog.message
        print(f"[ALERT MESSAGE] {alert_text}")
        assert alert_text == "✅ User created successfully!", \
            f"Expecting text '✅ User created successfully!', received '{alert_text}'"

        dialog.accept()
        page.wait_for_timeout(2000)

        page.reload()  # check user on UI
        page.get_by_text("All Users").click()
        page.wait_for_timeout(2000)
        page.get_by_text(new_user.username).wait_for(state="visible", timeout=5000)

        users = admin_steps.get_all_users().json()  # check in API
        assert new_user.username in [u["username"] for u in users], \
            f"User '{new_user.username}' not found in API"

        context.close()
        browser.close()


@allure.title("admin login with incorrect data test")
@allure.description("Test admin cannot create user with invalid username")
def test_admin_can_login_with_un_correct_data():
    admin_steps = AdminSteps([])
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    base_url = "http://localhost:3000"
    new_user = RandomModelGenerator.generate(CreateUserRequest)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir="videos/")
        page = context.new_page()

        page.goto(base_url)  # 1 step login admin
        page.get_by_placeholder("Username").fill(admin.username)
        page.get_by_placeholder("Password").fill(admin.password)
        page.locator("button").click()
        page.get_by_text("Admin Panel").wait_for(state="visible")

        page.get_by_placeholder("Username").fill('AK')  # 2 step create user with invalid username
        page.get_by_placeholder("Password").fill(new_user.password)

        with page.expect_event("dialog") as dialog_info:  # Check alert
            page.get_by_role("button", name="Add User").click()

        dialog: Dialog = dialog_info.value
        alert_text = dialog.message
        print(f"[ALERT MESSAGE] {alert_text}")
        assert "Username must be between 3 and 15 characters" in alert_text, \
            f"Expected error message about username length, received: '{alert_text}'"

        dialog.accept()
        page.wait_for_timeout(2000)

        page.reload()  # check user on UI
        page.get_by_text("All Users").click()
        page.wait_for_timeout(2000)
        assert page.get_by_text('AK').count() == 0, \
            "User 'AK' should not be visible in UI"

        users = admin_steps.get_all_users().json()
        assert 'AK' not in [u["username"] for u in users], \
            "User 'AK' should not exist in API"

        context.close()
        browser.close()

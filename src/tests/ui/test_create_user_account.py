import base64
import os
import re

import allure
import requests
from playwright.sync_api import sync_playwright, Dialog

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.api.steps.user_steps_model import UserSteps

os.makedirs("screenshots", exist_ok=True)
os.makedirs("videos", exist_ok=True)


@allure.title("user creates account by UI test")
@allure.description("Test user account creation through UI after API setup")
def test_user_can_create_account_by_ui():
    admin_steps = AdminSteps([])  # login by admin

    new_user = RandomModelGenerator.generate(CreateUserRequest)  # create user by admin
    created_user = admin_steps.create_user(new_user)

    user_steps = UserSteps([])  # User login
    user_steps.login(new_user)

    credentials = f"{new_user.username}:{new_user.password}"
    auth_token = "Basic " + base64.b64encode(credentials.encode()).decode()

    base_url = "http://localhost:3000"
    dashboard_url = "http://localhost:3000/dashboard"
    accounts_url = "http://localhost:4111/api/v1/customer/accounts"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir="videos/")
        page = context.new_page()

        page.goto(base_url)  # authorization by user
        page.evaluate(f"""
            localStorage.setItem('authToken', '{auth_token}');
        """)

        page.goto(f"{dashboard_url}")  # push button by user
        page.get_by_text("User Dashboard").wait_for(state="visible", timeout=5000)

        with page.expect_event("dialog") as dialog_info:  # Check alert
            page.get_by_role("button", name="➕ Create New Account").click()

        dialog: Dialog = dialog_info.value
        alert_text = dialog.message
        print(f"[ALERT MESSAGE] {alert_text}")

        assert "New Account Created!" in alert_text, \
            f"Expecting 'New Account Created!' in alert, received '{alert_text}'"  # checking the account number
        assert re.search(r"Account Number: ACC\d+", alert_text), \
            f"Expected account number in format 'ACCX' in alert, received '{alert_text}'"

        match = re.match(r".*Account Number: (\w+)", alert_text)  # extracting the account number from the alert text
        assert match, f"No account number found in '{alert_text}'"

        created_acc_number = match.group(1)

        dialog.accept()  # accept alert
        page.wait_for_timeout(2000)

        headers = {"Authorization": auth_token}
        response = requests.get(accounts_url, headers=headers, timeout=10)
        response.raise_for_status()
        accounts = response.json()
        print(f"[DEBUG] Accounts from API: {accounts}")

        created_account = next((acc for acc in accounts if acc.get("accountNumber") == created_acc_number), None)

        assert created_account is not None, f"Account with number '{created_acc_number}' not found in API response"
        assert created_account["balance"] == 0.0, "Initial balance should be 0.0"
        assert len(accounts) > 0, "No accounts found after creation"

        context.close()
        browser.close()

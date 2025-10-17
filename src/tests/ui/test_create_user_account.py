import base64
import re
import requests
from playwright.sync_api import Dialog
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.api.steps.user_steps_model import UserSteps


def test_user_can_create_account_by_ui(browser_context, config, page_objects):
    login_page = page_objects["login"]
    dashboard_page = page_objects["dashboard"]

    admin_steps = AdminSteps([])  # Login by admin
    new_user = RandomModelGenerator.generate(CreateUserRequest)  # Create user by admin
    created_user = admin_steps.create_user(new_user)

    user_steps = UserSteps([])  # User login
    user_steps.login(new_user)

    credentials = f"{new_user.username}:{new_user.password}"
    auth_token = "Basic " + base64.b64encode(credentials.encode()).decode()

    accounts_url = f"{config['backend_url']}/customer/accounts"

    # Authorization by user
    login_page.open_login_page()
    browser_context.evaluate(f"localStorage.setItem('authToken', '{auth_token}');")

    # Navigate to dashboard and create account
    dashboard_page.open_user_page()
    assert dashboard_page.is_user_dashboard_visible()

    with browser_context.expect_event("dialog") as dialog_info:  # Check alert
        dashboard_page.click_create_new_account()

    dialog: Dialog = dialog_info.value
    alert_text = dialog.message
    print(f"[ALERT MESSAGE] {alert_text}")

    assert "New Account Created!" in alert_text, \
        f"Expecting 'New Account Created!' in alert, received '{alert_text}'"  # Checking the account number
    assert re.search(r"Account Number: ACC\d+", alert_text), \
        f"Expected account number in format 'ACCX' in alert, received '{alert_text}'"

    match = re.match(r".*Account Number: (\w+)", alert_text)  # Extracting the account number from the alert text
    assert match, f"No account number found in '{alert_text}'"

    created_acc_number = match.group(1)

    dialog.accept()  # Accept alert

    headers = {"Authorization": auth_token}
    response = requests.get(accounts_url, headers=headers)
    response.raise_for_status()
    accounts = response.json()
    print(f"[DEBUG] Accounts from API: {accounts}")

    created_account = next((acc for acc in accounts if acc.get("accountNumber") == created_acc_number), None)

    assert created_account is not None, f"Account with number '{created_acc_number}' not found in API response"
    assert created_account["balance"] == 0.0, "Initial balance should be 0.0"
    assert len(accounts) > 0, "No accounts found after creation"

from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.api.steps.user_steps_model import UserSteps
from src.main.ui.page_object.handle_dialog import DialogHelper


def test_user_can_create_account_by_ui(browser_context, config, page_objects, new_user):
    AdminSteps([]).create_user(new_user)
    UserSteps([]).login(new_user)  # User login

    page_objects["login"].auth_as_user(new_user.username, new_user.password)
    page_objects["dashboard"].open_user_page()
    assert page_objects["dashboard"].is_user_dashboard_visible(), "Dashboard should be visible"

    # Navigate to dashboard and create account
    page_objects["dashboard"].open_user_page()
    assert page_objects["dashboard"].is_user_dashboard_visible()

    with browser_context.expect_event("dialog") as dialog_info:  # Check alert
        page_objects["dashboard"].click_create_new_account()

    created_acc_number = DialogHelper.extract_account_number(dialog_info)

    accounts = UserSteps([]).get_all_customer_accounts(new_user).json()
    print(f"[DEBUG] Accounts from API: {accounts}")

    created_account = next((acc for acc in accounts if acc.get("accountNumber") == created_acc_number), None)

    assert created_account is not None, f"Account with number '{created_acc_number}' not found in API response"
    assert created_account["balance"] == 0.0, "Initial balance should be 0.0"
    assert len(accounts) > 0, "No accounts found after creation"

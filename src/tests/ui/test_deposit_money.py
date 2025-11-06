from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.api.steps.user_steps_model import UserSteps
from src.main.ui.page_object.handle_dialog import DialogHelper


def test_user_make_deposit_by_ui(browser_context, config, page_objects, new_user):
    AdminSteps([]).create_user(new_user)
    UserSteps([]).login(new_user).create_account(new_user)

    page_objects["login"].auth_as_user(new_user.username, new_user.password)
    page_objects["dashboard"].open_user_page()
    page_objects["dashboard"].click_deposit_money()
    assert page_objects["deposit"].is_deposit_money_page_visible()

    deposit_amount = "500.50"
    with browser_context.expect_event("dialog") as dialog_info:
        page_objects["deposit"].make_deposit(created_acc_number, deposit_amount)

    DialogHelper.assert_dialog_contains_text(dialog_info, "Deposit successful")
    deposited_account = next((acc for acc in accounts if acc.get("accountNumber") == created_acc_number), None)

    assert deposited_account is not None, f"Account with number '{created_acc_number}' not found in API response"
    assert deposited_account["balance"] == float(deposit_amount), f"Balance should be {deposit_amount}"
    assert deposited_account["id"] == created_acc_number, "Account ID should match"

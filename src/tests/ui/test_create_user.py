from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.ui.page_object.admin_panel_page import AdminPanel
from src.main.ui.page_object.handle_dialog import DialogHelper


def test_admin_create_user(browser_context, page_objects):
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    new_user = RandomModelGenerator.generate(CreateUserRequest)

    page_objects["login"].open_login_page().login(admin.username, admin.password)  # Admin Login
    assert page_objects["admin"].is_admin_panel_visible()

    page_objects["admin"].open_admin_page()  # Create user
    with browser_context.expect_event("dialog") as dialog_info:
        page_objects["admin"].create_new_user(new_user.username, new_user.password)

    DialogHelper.assert_dialog_exact_text(dialog_info, AdminPanel.SUCCESS_USER_CREATED)  # Check alert with expected success message

    browser_context.reload()  # Check user on UI
    page_objects["admin"].all_user_visible()
    browser_context.get_by_text(new_user.username).wait_for(state="visible")

    users = AdminSteps([]).get_all_users().json()  # Check user in API
    assert new_user.username in [u["username"] for u in users], \
        f"User '{new_user.username}' not found in API"


def test_admin_create_invalid_user(browser_context, page_objects):
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    new_user = RandomModelGenerator.generate(CreateUserRequest)

    page_objects["login"].open_login_page().login(admin.username, admin.password)  # Login admin
    assert page_objects["admin"].is_admin_panel_visible(), "Admin Panel should be visible"

    page_objects["admin"].open_admin_page()  # Create user
    with browser_context.expect_event("dialog") as dialog_info:
        page_objects["admin"].create_new_user("AK", new_user.password)

    DialogHelper.assert_dialog_contains_text(dialog_info, AdminPanel.ERROR_USERNAME_LENGTH)  # Check alert contains error message

    browser_context.reload()  # Check user on UI
    assert page_objects["admin"].all_user_visible(), "All Users section should be visible"
    assert browser_context.get_by_text("AK").count() == 0, \
        "User 'AK' should not be visible in UI"

    users = AdminSteps([]).get_all_users().json()  # Check user in API
    assert "AK" not in [u["username"] for u in users], \
        "User 'AK' should not exist in API"

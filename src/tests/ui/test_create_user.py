from playwright.sync_api import Dialog
from src.main.ui.page_object.admin_panel_page import AdminPanel
from src.main.ui.page_object.login_page import LoginPage
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps


def test_admin_create_user(browser_context, page_objects):
    login_page = page_objects["login"]
    admin_panel = page_objects["admin"]
    admin_steps = AdminSteps([])
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    new_user = RandomModelGenerator.generate(CreateUserRequest)

    login_page.open_login_page()  # Login admin
    login_page.login(admin.username, admin.password)
    assert admin_panel.is_admin_panel_visible()

    admin_panel.open_admin_page()  # Create user
    with browser_context.expect_event("dialog") as dialog_info:
        admin_panel.create_new_user(new_user.username, new_user.password)

    dialog: Dialog = dialog_info.value  # Check alert
    alert_text = dialog.message
    print(f"[ALERT MESSAGE] {alert_text}")
    assert alert_text == "✅ User created successfully!", \
        f"Expecting text '✅ User created successfully!', received '{alert_text}'"
    dialog.accept()

    browser_context.reload()  # Check user on UI
    admin_panel.all_user_visible()
    browser_context.get_by_text(new_user.username).wait_for(state="visible")

    users = admin_steps.get_all_users().json()  # Check user in API
    assert new_user.username in [u["username"] for u in users], \
        f"User '{new_user.username}' not found in API"


def test_admin_create_invalid_user(browser_context, page_objects):
    login_page = page_objects["login"]
    admin_panel = page_objects["admin"]
    admin_steps = AdminSteps([])
    admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
    new_user = RandomModelGenerator.generate(CreateUserRequest)

    login_page.open_login_page()   # Login admin
    login_page.login(admin.username, admin.password)
    assert admin_panel.is_admin_panel_visible(), "Admin Panel should be visible"

    admin_panel.open_admin_page()   # Create user
    with browser_context.expect_event("dialog") as dialog_info:
        admin_panel.create_new_user("AK", new_user.password)

    dialog: Dialog = dialog_info.value   # Check alert
    alert_text = dialog.message
    print(f"[ALERT MESSAGE] {alert_text}")
    assert "Username must be between 3 and 15 characters" in alert_text, \
        f"Expected error message about username length, received: '{alert_text}'"
    dialog.accept()

    browser_context.reload()    # Check user on UI
    assert admin_panel.all_user_visible(), "All Users section should be visible"
    assert browser_context.get_by_text("AK").count() == 0, \
        "User 'AK' should not be visible in UI"

    users = admin_steps.get_all_users().json()  # Check user in API
    assert "AK" not in [u["username"] for u in users], \
        "User 'AK' should not exist in API"

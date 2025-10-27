from src.main.api.steps.admin_steps_model import AdminSteps


def test_admin_can_login_with_correct_data(page_objects):
    page_objects["login"].open_login_page().login("admin", "admin")
    assert page_objects["admin"].is_admin_panel_visible()


def test_user_can_login_with_correct_data(page_objects, new_user):
    AdminSteps([]).create_user(new_user)
    page_objects["login"].open_login_page().login(new_user.username, new_user.password)
    assert page_objects["dashboard"].is_user_dashboard_visible()

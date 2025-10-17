from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.ui.page_object.login_page import LoginPage


def test_admin_can_login_with_correct_data(page_objects):
    login_page = page_objects["login"]
    admin_panel = page_objects["admin"]

    login_page.open_login_page()
    login_page.login("admin", "admin")
    assert admin_panel.is_admin_panel_visible()


def test_user_can_login_with_correct_data(page_objects):
    login_page = page_objects["login"]
    dashboard_page = page_objects["dashboard"]
    admin_steps = AdminSteps([])

    user_request = RandomModelGenerator.generate(CreateUserRequest)
    admin_steps.create_user(user_request)

    login_page.open_login_page()
    login_page.login(user_request.username, user_request.password)

    assert dashboard_page.is_user_dashboard_visible()


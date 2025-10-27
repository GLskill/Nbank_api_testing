from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.steps.admin_steps_model import AdminSteps
from src.main.ui.page_object.login_page import LoginPage


def test_admin_can_login_with_correct_data(page_objects):
    page_objects["login"].open_login_page().login("admin", "admin")
    assert page_objects["admin"].is_admin_panel_visible()


def test_user_can_login_with_correct_data(page_objects):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    AdminSteps([]).create_user(user_request)
    page_objects["login"].open_login_page().login(user_request.username, user_request.password)
    assert page_objects["dashboard"].is_user_dashboard_visible()


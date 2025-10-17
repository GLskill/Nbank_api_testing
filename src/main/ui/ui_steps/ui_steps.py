from playwright.sync_api import Page, Dialog

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


class UiSteps:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.locator("button")

    def navigate_to_page(self):
        self.page.goto('http://localhost:3000')

    def admin_login(self, username: str, password: str):
        admin = CreateUserRequest(username="admin", password="admin", role="ADMIN")
        self.username_input.fill(admin.username)
        self.password_input.fill(admin.password)
        self.login_button.click()
        self.page.get_by_text("Admin Panel").wait_for(state="visible")

    def admin_create_user_after_login(self):
        new_user = RandomModelGenerator.generate(CreateUserRequest)
        self.page.get_by_placeholder("Username").fill(new_user.username)  # 2 step  create user
        self.page.get_by_placeholder("Password").fill(new_user.password)
        with self.page.expect_event("dialog") as dialog_info:  # Check alert
            self.page.get_by_role("button", name="Add User").click()

        dialog: Dialog = dialog_info.value
        alert_text = dialog.message
        print(f"[ALERT MESSAGE] {alert_text}")
        assert alert_text == "✅ User created successfully!", \
            f"Expecting text '✅ User created successfully!', received '{alert_text}'"
        dialog.accept()

    def user_login(self, username: str, password: str):
        new_user = RandomModelGenerator.generate(CreateUserRequest)
        self.username_input.fill(new_user.username)
        self.password_input.fill(new_user.password)
        self.login_button.click()
        self.page.get_by_text("User Dashboard").wait_for(state="visible")








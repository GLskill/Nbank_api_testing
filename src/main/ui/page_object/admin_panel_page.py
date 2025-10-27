from playwright.sync_api import Page
from src.main.ui.page_object.base_page import BasePage


class AdminPanel(BasePage):
    SUCCESS_USER_CREATED = "✅ User created successfully!"
    ERROR_USERNAME_LENGTH = "Username must be between 3 and 15 characters"

    def __init__(self, page: Page, frontend_url: str):
        super().__init__(page, frontend_url)

    def open_admin_page(self):
        self.page.goto(f'{self.frontend_url}/admin')
        return self

    def is_admin_panel_visible(self):
        return self.page.locator("text=Admin Panel").is_visible()

    def all_user_visible(self):
        return self.page.locator("text=All Users").is_visible()

    @property
    def button_add_user(self):
        return self.page.get_by_role("button", name="Add User")

    @property
    def username_input(self):
        return self.page.get_by_placeholder('Username')

    @property
    def password_input(self):
        return self.page.get_by_placeholder('Password')

    def create_new_user(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.button_add_user.click()
        return self

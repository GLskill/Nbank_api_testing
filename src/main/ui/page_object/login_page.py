from playwright.sync_api import Page
from src.main.ui.page_object.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page, frontend_url: str):
        super().__init__(page, frontend_url)

    def open_login_page(self):
        self.page.goto(f'{self.frontend_url}/login')
        return self

    def is_login_visible(self):
        return self.page.locator("text=Login").is_visible()

    @property
    def username_input(self):
        return self.page.get_by_placeholder('Username')

    @property
    def password_input(self):
        return self.page.get_by_placeholder('Password')

    @property
    def button_login_visible(self):
        return self.page.get_by_role("button", name="Login")

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.button_login_visible.click()
        return self





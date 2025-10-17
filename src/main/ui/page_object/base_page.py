from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, frontend_url: str):
        self.page = page
        self.frontend_url = frontend_url

    def is_logo_visible(self):
        return self.page.locator("text=NoBugs Bank").is_visible()

    def login_button(self):
        self.page.get_by_role("button", name="Login").click()
        return self

    def logout_button(self):
        self.page.get_by_role("button", name="🚪 Logout").click()
        return self

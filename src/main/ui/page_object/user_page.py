from playwright.sync_api import Page

from src.main.ui.page_object.base_page import BasePage


class UserPage(BasePage):
    def __init__(self, page: Page, frontend_url: str):
        super().__init__(page, frontend_url)

    def open_user_page(self):
        self.page.goto(f'{self.frontend_url}/dashboard')
        return self

    def is_user_dashboard_visible(self):
        return self.page.locator("text=User Dashboard").is_visible()

    @property
    def deposit_money(self):
        return self.page.get_by_role("button", name="💰 Deposit Money")

    def click_deposit_money(self):
        self.deposit_money.click()
        return self

    @property
    def make_transfer(self):
        return self.page.get_by_role("button", name="🔄 Make a Transfer")

    def click_make_transfer(self):
        self.make_transfer.click()
        return self

    @property
    def create_new_account(self):
        return self.page.get_by_role("button", name="➕ Create New Account")

    def click_create_new_account(self):
        self.create_new_account.click()
        return self

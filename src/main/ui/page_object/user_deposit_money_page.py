from playwright.sync_api import Page
from src.main.ui.page_object.base_page import BasePage


class UserDepositMoneyPage(BasePage):
    def __init__(self, page: Page, frontend_url: str):
        super().__init__(page, frontend_url)

    def open_user_deposit_money_page(self):
        self.page.goto(f'{self.frontend_url}/deposit')
        return self

    def is_deposit_money_page_visible(self):
        return self.page.locator("text=💰 Deposit Money").is_visible()

    @property
    def account_selector(self):
        return self.page.locator("select").first

    @property
    def amount_input(self):
        return self.page.get_by_placeholder("Enter amount")

    @property
    def deposit_button(self):
        return self.page.get_by_role("button", name="💵 Deposit")

    def wait_for_accounts_to_load(self):
        """Ждём, пока в dropdown появятся аккаунты (не только placeholder)"""
        self.page.wait_for_function(
            "document.querySelector('select option:nth-child(2)') !== null",
            timeout=10000
        )
        return self

    def select_account(self, account_name: str):
        if account_name.startswith("ACC"):
            account_id = account_name.replace("ACC", "")
        else:
            account_id = account_name

        self.account_selector.select_option(value=account_id)
        return self

    def enter_amount(self, amount: str):
        self.amount_input.fill(amount)
        return self

    def click_deposit(self):
        self.deposit_button.click()
        return self

    def make_deposit(self, account: str, amount: str):
        self.wait_for_accounts_to_load()  # Ждём загрузки аккаунтов
        self.select_account(account)
        self.enter_amount(amount)
        self.click_deposit()
        return self

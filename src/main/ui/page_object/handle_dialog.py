import re
from typing import Any
from playwright.sync_api import Dialog


class DialogHelper:
    @staticmethod
    def handle_dialog(dialog_info: Any, auto_accept: bool = True) -> str:
        dialog: Dialog = dialog_info.value
        alert_text = dialog.message
        print(f"[ALERT MESSAGE] {alert_text}")
        if auto_accept:
            dialog.accept()
        return alert_text

    @staticmethod
    def assert_dialog_exact_text(dialog_info: Any, expected_text: str, auto_accept: bool = True):
        alert_text = DialogHelper.handle_dialog(dialog_info, auto_accept)
        assert alert_text == expected_text, \
            f"Expecting text '{expected_text}, recived '{alert_text}'"

    @staticmethod
    def assert_dialog_contains_text(dialog_info: Any, expected_substring: str, auto_accept: bool = True):
        alert_text = DialogHelper.handle_dialog(dialog_info, auto_accept)
        assert expected_substring in alert_text, \
            f"Expected '{expected_substring}' in alert, received '{alert_text}'"

    @staticmethod
    def extract_account_number(dialog_info: Any, auto_accept: bool = True) -> str:
        alert_text = DialogHelper.handle_dialog(dialog_info, auto_accept=auto_accept)
        assert "New Account Created!" in alert_text, \
            f"Expecting 'New Account Created!' in alert, received '{alert_text}'"
        assert re.search(r"Account Number: ACC\d+", alert_text), \
            f"Expected account number in format 'ACCX' in alert, received '{alert_text}'"
        match = re.match(r".*Account Number: (\w+)", alert_text)
        assert match, f"No account number found in '{alert_text}'"

        account_number = match.group(1)
        return account_number

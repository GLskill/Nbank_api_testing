import pytest
import requests


@pytest.mark.api
class TestCreateAccount:
    @pytest.mark.debug
    def test_create_account(self):
        create_user_response = requests.post(
            url='http://localhost:4111/api/v1/admin/users',
            json={
                "username": "katee1998ak1",
                "password": "verysTRongPassword33$",
                "role": "USER"
            },
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Basic YWRtaW46YWRtaW4='
            }
        )

        assert create_user_response.status_code == 201

        login_response = requests.post(
            url='http://localhost:4111/api/v1/auth/login',
            json={
                "username": "katee1998ak1",
                "password": "verysTRongPassword33$",
            },
        )

        assert login_response.status_code == 200
        authorization_token = login_response.headers.get('authorization')
        assert authorization_token

        create_account_response = requests.post(
            url='http://localhost:4111/api/v1/accounts',
            headers={
                'Accept': 'application/json',
                'Authorization': authorization_token
            }
        )

        assert create_account_response.status_code == 201
        assert create_account_response.json().get('balance') == 0.0
        assert not create_account_response.json().get('transactions')

        get_account_response = requests.get(
            url='http://localhost:4111/api/v1/accounts',
            headers={
                'Accept': 'application/json',
                'Authorization': authorization_token
            }
        )

        assert get_account_response.status_code == 200
        assert get_account_response.json().get('balance') == 0.0
        assert not get_account_response.json().get('transactions')


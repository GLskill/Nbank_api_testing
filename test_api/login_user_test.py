import pytest
import requests


@pytest.mark.api
class TestLoginUser:
    @pytest.mark.debug
    def test_login_user(self):
        create_user_response = requests.post(
            url='http://localhost:4111/api/v1/admin/users',
            json={
                "username": "katee1998",
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
                "username": "katee1998",
                "password": "verysTRongPassword33$",
            },
        )

        assert login_response.status_code == 200
        assert login_response.headers.get('authorization')

    def test_login_admin_user(self):
        login_response = requests.post(
            url='http://localhost:4111/api/v1/auth/login',
            json={
                "username": "admin",
                "password": "admin",
            }
        )

        assert login_response.status_code == 200
        assert login_response.headers.get('authorization') == 'Basic YWRtaW46YWRtaW4='

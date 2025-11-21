import pytest
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture
def admin_user():
    """Фикстура для создания admin пользователя"""
    return CreateUserRequest(username="admin", password="admin", role="ADMIN")


@pytest.fixture
def new_user():
    """Фикстура для создания случайного пользователя"""
    return RandomModelGenerator.generate(CreateUserRequest)

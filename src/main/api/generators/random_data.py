import random
import os
import uuid
from faker import Faker

faker = Faker()


class RandomData:
    @staticmethod
    def get_username() -> str:
        # UUID гарантирует уникальность даже при параллельных запусках
        unique_id = str(uuid.uuid4())[:8]  # Первые 8 символов UUID
        base_name = ''.join(faker.random_letters(length=random.randint(3, 6)))
        return f"{base_name}{unique_id}"  # Например: aBcXyz12a4f5

    @staticmethod
    def get_deposit_amount(min_value: float = 1.0, max_value: float = 100000.0) -> float:
        return random.uniform(min_value, max_value)

    @staticmethod
    def get_password() -> str:
        upper = [letter.upper() for letter in faker.random_letters(length=3)]
        lower = [letter.lower() for letter in faker.random_letters(length=3)]
        digits = [str(faker.random_digit()) for _ in range(3)]
        special = [random.choice('!@#$%^&')]
        password = upper + lower + digits + special
        random.shuffle(password)
        return ''.join(password)


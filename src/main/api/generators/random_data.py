import random

from faker import Faker

faker = Faker()


class RandomData:
    @staticmethod
    def get_username() -> str:
        return ''.join(faker.random_letters(length=random.randint(3, 15)))

    @staticmethod
    def get_deposit_amount(min_value: float = 1.0, max_value: float = 100000.0) -> float:
        return random.uniform(min_value, max_value)

    @staticmethod
    def get_password() -> str:
        upper = [letter.upper() for letter in faker.random_letters(length=3)]
        lower = [letter.lower() for letter in faker.random_letters(length=3)]
        digits = [str(faker.random_digit()) for _ in range(3)]
        special = [random.choice('!@#$%^&*')]
        return random.shuffle(upper + lower + digits + special)

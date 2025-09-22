import random
import string

from faker import Faker

faker = Faker()


class RandomData:
    @staticmethod
    def get_username() -> str:
        return ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 15)))

    @staticmethod
    def get_deposit_amount(min_value: float = 1.0, max_value: float = 100000.0) -> float:
        return random.uniform(min_value, max_value)

    @staticmethod
    def get_password() -> str:
        upper = [random.choice(string.ascii_letters).upper() for _ in range(3)]
        lower = [random.choice(string.ascii_letters).lower() for _ in range(3)]
        digits = [str(faker.random_digit()) for _ in range(3)]
        special = [random.choice('!@#$%^&')]
        password = upper + lower + digits + special
        random.shuffle(password)
        return ''.join(password)

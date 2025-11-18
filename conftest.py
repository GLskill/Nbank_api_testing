from time import sleep
from src.main.api.fixtures.api_fixtures import *
from src.main.api.fixtures.user_fixtures import *
from src.main.api.fixtures.object_fixtures import *
import requests
from src.main.api.configs.config import Config


@pytest.fixture(scope="session", autouse=True)
def healthcheck():
    logging.info("backend healthcheck")
    for _ in range(5):
        try:
            requests.get(f"{Config.get('server')}")  # wait til connection can be established
            return
        except requests.exceptions.ConnectionError as e:
            logging.error(e)
        sleep(1)
    raise AssertionError("backend health check failed")

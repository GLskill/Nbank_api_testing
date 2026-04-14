import random
import time
from time import sleep

import requests

from src.main.api.fixtures.user_fixtures import *
from src.main.api.fixtures.api_fixtures import *
from src.main.api.fixtures.object_fixtures import *
from src.main.api.fixtures.deposit_fixtures import *
from src.main.api.fixtures.transfer_fixtures import *
from src.main.ui.fixtures.ui_browser_close_fixtures import *
from src.main.ui.fixtures.base_steps_fixtures import *


def _apply_global_seed(seed: int) -> None:
    random.seed(seed)
    try:
        from faker import Faker
        Faker.seed(seed)
    except Exception:
        pass

    try:
        from src.main.api.generators import random_data
        if hasattr(random_data, "faker"):
            random_data.faker.seed_instance(seed)
    except Exception:
        pass


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--seed",
        action="store",
        default=os.getenv("PYTEST_SEED"),
        help="..."
    )


def pytest_configure(config: pytest.Config) -> None:
    seed = None
    if hasattr(config, "workerinput"):
        seed = config.workerinput.get("seed")

    if seed is None:
        opt = config.getoption("--seed")
        seed = int(opt) if opt is not None else int(time.time_ns() % 2_000_000_000)

    config._nbank_seed = int(seed)
    _apply_global_seed(int(seed))


def pytest_configure_node(node) -> None:
    seed = getattr(node.config, "_nbank_seed", None)
    if seed is not None:
        node.workerinput["seed"] = int(seed)


def pytest_collection_finish(session: pytest.Session) -> None:
    config = session.config
    base_seed = getattr(config, '_nbank_seed', None)
    if base_seed is None:
        return
    workerid = None
    if hasattr(config, "workerinput"):
        workerid = config.workerinput.get("workerid")
    if workerid and str(workerid).startswith("gw"):
        try:
            idx = int(str(workerid)[2:])
        except Exception:
            idx = 0
        runtime_seed = int(base_seed) + (idx + 1) * 1_000_000
    else:
        runtime_seed = int(base_seed)

    _apply_global_seed(runtime_seed)

    # Опционально: логи для дебага
    print(f"[{workerid or 'main'}] Using seed: {runtime_seed}")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # API конфигурация
    server = os.getenv("SERVER", "http://localhost:4111/api")
    api_version = os.getenv("API_VERSION", "/v1")
    base_api_url = os.getenv("BASE_API_URL", "http://localhost:4111")

    # UI конфигурация - UI_BASE_URL имеет приоритет
    ui_base_url = os.getenv("UI_BASE_URL")
    base_ui_url = os.getenv("BASE_UI_URL")

    # Определяем финальный UI URL
    final_ui_url = ui_base_url or base_ui_url or "http://localhost:3000"

    # Устанавливаем все варианты для совместимости
    os.environ["SERVER"] = server
    os.environ["API_VERSION"] = api_version
    os.environ["UI_BASE_URL"] = final_ui_url
    os.environ["BASE_API_URL"] = base_api_url
    os.environ["BASE_UI_URL"] = final_ui_url

    print(f"\n{'=' * 60}")
    print(f"Test Environment Configuration:")
    print(f"  SERVER:        {server}")
    print(f"  API_VERSION:   {api_version}")
    print(f"  Full API URL:  {server}{api_version}")
    print(f"  UI_BASE_URL:   {final_ui_url}")
    print(f"  BASE_API_URL:  {base_api_url}")
    print(f"  BASE_UI_URL:   {final_ui_url}")
    print(f"{'=' * 60}\n")

    yield


@pytest.fixture(scope="session", autouse=True)
def healthcheck(setup_test_environment):
    """
    Проверка доступности backend перед запуском тестов.
    Зависит от setup_test_environment чтобы переменные были установлены.
    """
    server = os.getenv("SERVER", "http://localhost:4111/api")

    # Формируем URL для healthcheck
    if server.endswith('/api'):
        health_url = f"{server}/health"
    else:
        health_url = f"{server}/api/health"

    logging.info(f"Backend healthcheck: {health_url}")

    # Учетные данные для health check
    headers = {
        "Authorization": "Basic YWRtaW46YWRtaW4="  # admin:admin в base64
    }

    for attempt in range(1, 11):
        try:
            # ✅ ВАЖНО: передаём headers в запрос!
            response = requests.get(health_url, headers=headers, timeout=5)
            if response.status_code == 200:
                logging.info(f"✓ Backend is ready at {health_url}")
                return
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt}/10 failed: {e}")
        sleep(2)

    logging.error(f"❌ Backend health check failed after 10 attempts: {health_url}")

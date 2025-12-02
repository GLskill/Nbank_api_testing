import os
from pathlib import Path


class Config:
    _instance = None
    _properties = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)

            config_path = Path(__file__).parents[4] / 'resources' / 'config.properties'

            if config_path.exists():
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            cls._properties[key.strip()] = value.strip()
            else:
                # Defaults если config.properties не найден
                cls._properties = {
                    'server': 'http://localhost:4111',
                    'api_version': '/api/v1',
                    'backendUrl': 'http://localhost:4111',
                    'frontendUrl': 'http://localhost:3000',
                    'browser': 'chromium',
                    'headless': 'true',
                    'timeout': '30000'
                }
        return cls._instance

    @staticmethod
    def get(key: str, default_value=None):
        """
        Получить значение конфигурации.
        Приоритет: ENV переменные > config.properties > defaults
        """
        # Специальная обработка для 'server'
        if key == 'server':
            # Проверяем SERVER из env
            env_server = os.environ.get('SERVER')
            if env_server:
                return env_server

            # Проверяем BASE_API_URL
            env_api = os.environ.get('BASE_API_URL')
            if env_api:
                # Убираем /api/v1 или /api если есть
                return env_api.replace('/api/v1', '').replace('/api', '')

            # Fallback на properties
            return Config()._properties.get(key, 'http://localhost:4111')

        # Специальная обработка для 'api_version'
        if key == 'api_version':
            env_version = os.environ.get('API_VERSION')
            if env_version:
                return env_version
            return Config()._properties.get(key, '/api/v1')

        # Специальная обработка для 'frontendUrl'
        if key == 'frontendUrl':
            # Проверяем UI_BASE_URL (приоритет)
            env_ui = os.environ.get('UI_BASE_URL')
            if env_ui:
                return env_ui

            # Проверяем BASE_UI_URL
            env_ui_alt = os.environ.get('BASE_UI_URL')
            if env_ui_alt:
                return env_ui_alt

            # Fallback на properties
            return Config()._properties.get(key, 'http://localhost:3000')

        # Для остальных ключей - стандартная логика
        env_value = os.environ.get(key.upper())
        if env_value:
            return env_value

        return Config()._properties.get(key, default_value)

    @staticmethod
    def get_api_base_url():
        """Получить полный URL для API: server + api_version"""
        server = Config.get('server')
        api_version = Config.get('api_version')
        return f"{server}{api_version}"

    @staticmethod
    def get_ui_base_url():
        """Получить URL для UI тестов"""
        return Config.get('frontendUrl')

    @staticmethod
    def print_config():
        """Вывести текущую конфигурацию"""
        print("\n" + "=" * 60)
        print("Config values:")
        print(f"  server:         {Config.get('server')}")
        print(f"  api_version:    {Config.get('api_version')}")
        print(f"  API Full URL:   {Config.get_api_base_url()}")
        print(f"  frontendUrl:    {Config.get('frontendUrl')}")
        print(f"  UI Base URL:    {Config.get_ui_base_url()}")
        print("=" * 60 + "\n")
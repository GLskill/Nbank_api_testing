import os
from pathlib import Path
from typing import Any


class Config:
    _instance = None
    _properties = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)

            # Попробуем найти config.properties в нескольких местах
            possible_paths = [
                Path(__file__).parents[3] / 'resources' / 'config.properties',
                Path(__file__).parents[4] / 'resources' / 'config.properties',
                Path.cwd() / 'resources' / 'config.properties',
                Path.cwd() / 'config.properties',
            ]

            config_path = None
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break

            # Если файл не найден, используем значения по умолчанию
            if config_path is None:
                print(f"Warning: config.properties not found. Using defaults and environment variables.")
                cls._properties = {
                    'server': 'http://localhost:4111',
                    'api_version': '/api/v1',
                    'backendUrl': 'http://localhost:4111',
                    'frontendUrl': 'http://localhost:3000',
                    'browser': 'chromium',
                    'headless': 'true',
                    'timeout': '30000'
                }
            else:
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            cls._properties[key.strip()] = value.strip()

        return cls._instance

    @staticmethod
    def get(key: str, default_value: Any = None):
        """
        Приоритет получения значений:
        1. Переменные окружения (BASE_API_URL, BASE_UI_URL)
        2. Переменные окружения с ключом key.upper()
        3. Значения из config.properties
        4. default_value
        """
        # Специальная обработка для server
        if key == 'server':
            env_val = os.environ.get('BASE_API_URL')
            if env_val:
                # Убираем /api/v1 или /api если он есть
                return env_val.replace('/api/v1', '').replace('/api', '')

        # Специальная обработка для frontendUrl
        if key == 'frontendUrl':
            env_val = os.environ.get('BASE_UI_URL')
            if env_val:
                return env_val

        # Стандартная проверка переменных окружения
        env_value = os.environ.get(key.upper())
        if env_value:
            return env_value

        # Значение из config.properties
        return Config()._properties.get(key, default_value)
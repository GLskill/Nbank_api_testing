import os
from pathlib import Path


class Config:
    _instance = None
    _properties = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)

            config_path = Path(__file__).parents[3] / 'resources' / 'config.properties'

            if config_path.exists():
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            cls._properties[key.strip()] = value.strip()
            else:
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
        if key == 'server':
            env_val = os.environ.get('BASE_API_URL')
            if env_val:
                return env_val.replace('/api/v1', '').replace('/api', '')

        if key == 'frontendUrl':
            env_val = os.environ.get('BASE_UI_URL')
            if env_val:
                return env_val

        env_value = os.environ.get(key.upper())
        if env_value:
            return env_value

        return Config()._properties.get(key, default_value)
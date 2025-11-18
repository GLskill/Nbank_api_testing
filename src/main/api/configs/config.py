import os
from pathlib import Path
from typing import Any


class Config:
    _instance = None
    _properties = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            config_path = Path(__file__).parents[3] / 'resources' / 'config.properties'
            if not config_path.exists():
                raise ImportError(f'Config file not found: {config_path}')
            with open(config_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        cls._properties[key.strip()] = value.strip()
        return cls._instance

    @staticmethod
    def get(key: str, default_value: Any = None):
        """
        Return environment variable value is set (key = KEY), if not searches for key in config.properties
        If nothing is found, returns default_value
        """
        env_value = os.environ.get(key.upper())
        if env_value:
            return env_value
        return Config()._properties.get(key, default_value)


#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации внутри контейнера
"""
import os
import json
from pathlib import Path

print("="*60)
print("CONFIGURATION CHECK")
print("="*60)

# Проверяем переменные окружения
print("\n1. Environment Variables:")
print(f"   BASE_API_URL = {os.getenv('BASE_API_URL', 'NOT SET')}")
print(f"   BASE_UI_URL = {os.getenv('BASE_UI_URL', 'NOT SET')}")
print(f"   TEST_PROFILE = {os.getenv('TEST_PROFILE', 'NOT SET')}")

# Проверяем config.json
print("\n2. config.json files:")
config_paths = [
    "/app/config.json",
    "/app/resources/config.json"
]

for path in config_paths:
    if Path(path).exists():
        print(f"\n   Found: {path}")
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            print(f"   backend_url  = {config.get('backend_url', 'NOT SET')}")
            print(f"   frontend_url = {config.get('frontend_url', 'NOT SET')}")
        except Exception as e:
            print(f"   ERROR reading: {e}")
    else:
        print(f"   Not found: {path}")

# Проверяем config.properties
print("\n3. config.properties files:")
props_paths = [
    "/app/config.properties",
    "/app/resources/config.properties"
]

for path in props_paths:
    if Path(path).exists():
        print(f"\n   Found: {path}")
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        print(f"   {line}")
        except Exception as e:
            print(f"   ERROR reading: {e}")
    else:
        print(f"   Not found: {path}")

# Проверяем структуру проекта
print("\n4. Project structure:")
print(f"   Current dir: {os.getcwd()}")
print(f"   /app contents:")
for item in sorted(Path("/app").iterdir()):
    print(f"     - {item.name}")

if Path("/app/resources").exists():
    print(f"   /app/resources contents:")
    for item in sorted(Path("/app/resources").iterdir()):
        print(f"     - {item.name}")

print("\n" + "="*60)
#!/usr/bin/env python3
import os
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "run.log")


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf8") as f:
        f.write(line + "\n")


def override_config_files():
    """Переопределяет localhost в config.json и config.properties на BASE_API_URL / BASE_UI_URL"""

    base_api_url = os.getenv("BASE_API_URL", "http://localhost:4111/api")
    base_ui_url = os.getenv("BASE_UI_URL", "http://localhost:3000")

    log(f"Environment variables:")
    log(f"  BASE_API_URL={base_api_url}")
    log(f"  BASE_UI_URL={base_ui_url}")

    # === 1. config.json ===
    config_json_paths = [
        Path("/app/config.json"),
        Path("/app/resources/config.json")
    ]

    for config_json_path in config_json_paths:
        if config_json_path.exists():
            try:
                with open(config_json_path, "r", encoding="utf8") as f:
                    config = json.load(f)

                old_backend = config.get("backend_url", "")
                old_frontend = config.get("frontend_url", "")

                config["backend_url"] = base_api_url.rstrip("/") + "/v1"  # /api/v1
                config["frontend_url"] = base_ui_url

                with open(config_json_path, "w", encoding="utf8") as f:
                    json.dump(config, f, indent=2)

                log(f"Updated {config_json_path}:")
                log(f"  backend_url: '{old_backend}' → '{config['backend_url']}'")
                log(f"  frontend_url: '{old_frontend}' → '{config['frontend_url']}'")
            except Exception as e:
                log(f"ERROR updating {config_json_path}: {e}")
        else:
            log(f"{config_json_path} not found — skipping")

    # === 2. config.properties ===
    config_props_paths = [
        Path("/app/config.properties"),
        Path("/app/resources/config.properties")
    ]

    for config_props_path in config_props_paths:
        if config_props_path.exists():
            try:
                with open(config_props_path, "r", encoding="utf8") as f:
                    lines = f.readlines()

                new_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("backendUrl="):
                        new_value = f"{base_api_url}/v1\n"
                        new_lines.append(f"backendUrl={base_api_url}/v1\n")
                        log(f"Updated {config_props_path}: backendUrl → {base_api_url}/v1")
                    elif stripped.startswith("frontendUrl="):
                        new_lines.append(f"frontendUrl={base_ui_url}\n")
                        log(f"Updated {config_props_path}: frontendUrl → {base_ui_url}")
                    elif stripped.startswith("server="):
                        server_url = base_api_url.split('/api')[0]
                        new_lines.append(f"server={server_url}\n")
                        log(f"Updated {config_props_path}: server → {server_url}")
                    elif stripped.startswith("api_version="):
                        new_lines.append("api_version=/api/v1\n")
                    else:
                        new_lines.append(line)

                with open(config_props_path, "w", encoding="utf8") as f:
                    f.writelines(new_lines)

            except Exception as e:
                log(f"ERROR updating {config_props_path}: {e}")
        else:
            log(f"{config_props_path} not found — skipping")


def main():
    # Создаём папки
    for d in ["/app/logs", "/app/test_results/html_reports",
              "/app/test_results/allure_results", "/app/test_results/screenshots"]:
        os.makedirs(d, exist_ok=True)

    profile = os.getenv("TEST_PROFILE", "api")
    log(f"Starting tests with profile: {profile}")

    # ПЕРЕОПРЕДЕЛЯЕМ КОНФИГИ ДО ЗАПУСКА ТЕСТОВ
    override_config_files()

    test_path = f"src/tests/{profile}"
    if not os.path.exists(test_path):
        log(f"ERROR: Test directory not found: {test_path}")
        sys.exit(1)

    cmd = [
        "pytest", test_path, "-v",
        "--html=/app/test_results/html_reports/report.html",
        "--self-contained-html",
        "--junitxml=/app/test_results/junit.xml",
        "--alluredir=/app/test_results/allure_results"
    ]

    env = os.environ.copy()
    env["TEST_PROFILE"] = profile
    env["PYTHONPATH"] = "/app"

    # Передаём URL как переменные окружения для тестов
    env["BASE_API_URL"] = os.getenv("BASE_API_URL", "http://localhost:4111/api")
    env["BASE_UI_URL"] = os.getenv("BASE_UI_URL", "http://localhost:3000")

    log(f"Running: {' '.join(cmd)}")
    log(f"Test environment:")
    log(f"  TEST_PROFILE={env['TEST_PROFILE']}")
    log(f"  BASE_API_URL={env['BASE_API_URL']}")
    log(f"  BASE_UI_URL={env['BASE_UI_URL']}")

    # Полное логирование
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    with open(LOG_FILE, "a", encoding="utf8") as f:
        for line in process.stdout:
            line = line.rstrip()
            print(line)
            f.write(line + "\n")

    process.wait()
    exit_code = process.returncode
    log(f"Tests finished with exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
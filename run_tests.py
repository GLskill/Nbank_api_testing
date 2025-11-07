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

    # === 1. config.json ===
    config_json_path = Path("/app/config.json")
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

            log(f"Updated config.json: backend_url='{old_backend}' → '{config['backend_url']}'")
            log(f"                 frontend_url='{old_frontend}' → '{config['frontend_url']}'")
        except Exception as e:
            log(f"ERROR updating config.json: {e}")
    else:
        log("config.json not found — skipping override")

    # === 2. config.properties ===
    config_props_path = Path("/app/config.properties")
    if config_props_path.exists():
        try:
            with open(config_props_path, "r", encoding="utf8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if line.strip().startswith("backendUrl="):
                    new_lines.append(f"backendUrl={base_api_url}/v1\n")
                    log(f"Updated config.properties: backendUrl → {base_api_url}/v1")
                elif line.strip().startswith("frontendUrl="):
                    new_lines.append(f"frontendUrl={base_ui_url}\n")
                    log(f"Updated config.properties: frontendUrl → {base_ui_url}")
                elif line.strip().startswith("server="):
                    new_lines.append(f"server={base_api_url.split('/api')[0]}\n")  # http://host.docker.internal:4111
                elif line.strip().startswith("api_version="):
                    new_lines.append("api_version=/api/v1\n")
                else:
                    new_lines.append(line)

            with open(config_props_path, "w", encoding="utf8") as f:
                f.writelines(new_lines)

        except Exception as e:
            log(f"ERROR updating config.properties: {e}")
    else:
        log("config.properties not found — skipping override")



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

    log(f"Running: {' '.join(cmd)}")

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


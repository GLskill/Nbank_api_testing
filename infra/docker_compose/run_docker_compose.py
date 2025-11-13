import subprocess
import json
import sys


def pull_browser_images():
    """Загружает образы браузеров из browsers.json"""
    print(">>> Docker pull все образы браузеров")

    try:
        with open('./config/browsers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        images = set()

        # Извлекаем все image из JSON
        def extract_images(obj):
            if isinstance(obj, dict):
                if 'image' in obj:
                    images.add(obj['image'])
                for value in obj.values():
                    extract_images(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_images(item)

        extract_images(data)

        # Загружаем каждый образ
        for image in images:
            print(f"Pulling {image}...")
            result = subprocess.run(['docker', 'pull', image],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ Ошибка при загрузке {image}: {result.stderr}")
            else:
                print(f"✓ {image} загружен")

    except FileNotFoundError:
        print("⚠️ Файл ./config/browsers.json не найден")
    except json.JSONDecodeError:
        print("❌ Ошибка чтения JSON файла")


def stop_docker_compose():
    """Останавливает Docker Compose"""
    print("\n>>> Остановить Docker Compose")
    result = subprocess.run(['docker', 'compose', 'down'],
                            capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"⚠️ Ошибка: {result.stderr}")


def start_docker_compose(detached=False):
    """Запускает Docker Compose"""
    print("\n>>> Запуск Docker Compose")

    cmd = ['docker', 'compose', 'up']
    if detached:
        cmd.append('-d')  # Запуск в фоновом режиме

    try:
        if detached:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.returncode == 0:
                print("✓ Docker Compose запущен в фоновом режиме")
            else:
                print(f"❌ Ошибка: {result.stderr}")
        else:
            # Запуск с выводом логов в реальном времени
            subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n>>> Остановка контейнеров...")
        stop_docker_compose()


def main():
    """Основная функция"""
    print("=== Перезапуск Docker Compose ===\n")

    # Останавливаем существующие контейнеры
    stop_docker_compose()

    # Загружаем образы браузеров
    pull_browser_images()

    # Запускаем Docker Compose
    # Используйте detached=True для запуска в фоновом режиме
    start_docker_compose(detached=False)


if __name__ == "__main__":
    main()


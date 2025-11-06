# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры для Playwright
RUN playwright install --with-deps chromium

# Копируем весь проект в контейнер
COPY . .

# Создаем директории для результатов
RUN mkdir -p /app/test_results/html_reports \
    /app/test_results/allure_results \
    /app/test_results/screenshots

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTEST_ADDOPTS="--tb=short"

# Команда по умолчанию - запуск всех тестов
CMD ["pytest", "src/tests/", "-v", \
     "--html=/app/test_results/html_reports/report.html", \
     "--self-contained-html", \
     "--junitxml=/app/test_results/junit.xml", \
     "--alluredir=/app/test_results/allure_results"]


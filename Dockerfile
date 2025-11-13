FROM python:3.13-slim-bookworm

ARG TEST_PROFILE=api
ARG BASE_API_URL=http://backend:4111/api
ARG BASE_UI_URL=http://frontend:3000

ENV TEST_PROFILE=${TEST_PROFILE}
ENV BASE_API_URL=${BASE_API_URL}
ENV BASE_UI_URL=${BASE_UI_URL}
ENV PYTHONPATH=/app
ENV PYTEST_ADDOPTS="--tb=short"

WORKDIR /app

# Устанавливаем curl для healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt run_tests.py ./

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pytest-html

# Устанавливаем зависимости для Playwright
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
        libgbm1 libasound2 libatspi2.0-0 libxshmfence1 \
    && playwright install chromium \
    && rm -rf /var/lib/apt/lists/*

# Создаём директории
RUN mkdir -p logs \
    && mkdir -p /app/test_results/html_reports \
               /app/test_results/allure_results \
               /app/test_results/screenshots \
    && chmod +x run_tests.py

COPY . .

CMD ["python", "run_tests.py"]
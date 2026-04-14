FROM python:3.13-slim-bookworm

ARG SERVER=http://localhost:4111/api
ARG UI_BASE_URL=http://localhost:3000

ENV SERVER=${SERVER}
ENV UI_BASE_URL=${UI_BASE_URL}
ENV PLAYWRIGHT_TEST_BASE_URL=${UI_BASE_URL}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN set -eux; \
    apt-get update -o Acquire::Retries=3 || \
    apt-get update -o Acquire::Retries=3 -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true; \
    playwright install-deps; \
    playwright install; \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p logs

COPY . .

USER root

CMD ["pytest", "-v", "--tb=short", "--alluredir", "allure-results"]

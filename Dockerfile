FROM python:3.13-slim-bookworm

ARG SERVER=http://localhost:4111/api
ARG UI_BASE_URL=http://localhost:3000

ENV SERVER=${SERVER}
ENV UI_BASE_URL=${UI_BASE_URL}

ENV PLAYWRIGHT_TEST_BASE_URL=${UI_BASE_URL}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && playwright install-deps
RUN playwright install

RUN mkdir -p logs

COPY . .

CMD pytest --log-level=DEBUG --log-cli-level=DEBUG --alluredir allure-results
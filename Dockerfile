FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && \
    playwright install-deps && \
    playwright install && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["pytest", "--alluredir", "allure-results"]
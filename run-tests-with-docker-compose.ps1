# run-tests-with-docker-compose.ps1

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$COMPOSE_FILE = "infra/docker_compose/docker-compose.yml"

Write-Host "Поднимаем тестовое окружение..."
docker compose -f $COMPOSE_FILE up -d

Write-Host "Ждем, пока backend станет доступен..."

while ($true) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4111/actuator/health" -Method Get
        if ($response.status -eq "UP") {
            break
        }
    } catch {
        # ещё не готов
    }
    Start-Sleep -Seconds 2
}

Write-Host "Backend готов!"

Write-Host "Запускаем тесты..."

docker run --rm `
  --network nbank-network `
  -e SERVER=http://backend:4111/api `
  -e API_VERSION=/v1 `
  -e BASE_API_URL=http://backend:4111 `
  -e UI_BASE_URL=http://frontend:80 `
  -e BASE_UI_URL=http://frontend:80 `
  -v "${PWD}/allure-results:/app/allure-results" `
  nbank-tests-glskill-latest

$TEST_EXIT_CODE = $LASTEXITCODE

Write-Host "Останавливаем окружение..."
docker compose -f $COMPOSE_FILE down

exit $TEST_EXIT_CODE

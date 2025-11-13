@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Nbank Test Runner - DEBUG MODE
echo ========================================
echo.

REM Устанавливаем профиль по умолчанию
if "%TEST_PROFILE%"=="" set TEST_PROFILE=api

echo Step 1: Check configuration inside container...
echo.

docker run --rm ^
  --add-host=host.docker.internal:host-gateway ^
  -e BASE_API_URL=http://host.docker.internal:4111/api ^
  -e BASE_UI_URL=http://host.docker.internal:3000 ^
  nbank-test-contenerv3 python check_config.py

echo.
echo ========================================
echo Step 2: Run actual tests
echo ========================================
echo.

if not exist "test_results" mkdir test_results
if not exist "test_results\html_reports" mkdir test_results\html_reports
if not exist "test_results\allure_results" mkdir test_results\allure_results
if not exist "logs" mkdir logs

docker run --rm --name test-runner ^
  --add-host=host.docker.internal:host-gateway ^
  -e TEST_PROFILE=%TEST_PROFILE% ^
  -e BASE_API_URL=http://host.docker.internal:4111/api ^
  -e BASE_UI_URL=http://host.docker.internal:3000 ^
  -v "%CD%\test_results:/app/test_results" ^
  -v "%CD%\logs:/app/logs" ^
  nbank-test-contenerv3

echo.
echo Done! Check logs\run.log for details
pause


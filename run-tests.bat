@echo off
echo Building Docker image...
docker build -t python-tests .

echo Creating directories...
if not exist "results" mkdir results
if not exist "logs" mkdir logs

echo Running tests...
docker run --rm ^
  -e TEST_PROFILE=api ^
  -e BASE_API_URL=http://host.docker.internal:4111/api ^
  -e BASE_UI_URL=http://host.docker.internal:3000 ^
  -v "%CD%\results:/app/test_results" ^
  -v "%CD%\logs:/app/logs" ^
  python-tests

echo Done! Check results/ and logs/
pause
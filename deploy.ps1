# deploy.ps1
Write-Host "Deploying Nbank application..." -ForegroundColor Green

$backendFile = "infra/kube/nbank-chart/templates/backend.yml"
$frontendFile = "infra/kube/nbank-chart/templates/frontend.yaml"

# Применяем манифесты
kubectl apply -f $backendFile
kubectl apply -f $frontendFile

# Ждем готовности подов
Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=backend --timeout=60s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=60s

# Показываем статус
Write-Host "`nDeployment status:" -ForegroundColor Cyan
kubectl get pods
kubectl get services

Write-Host "`nForwarding ports..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:4111" -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Yellow

# Запускаем port-forward в фоновых процессах
Start-Job -ScriptBlock { kubectl port-forward svc/backend 4111:4111 }
Start-Job -ScriptBlock { kubectl port-forward svc/frontend 3000:80 }

# Ждем немного чтобы порты пробросились
Start-Sleep -Seconds 3

Write-Host "`nApplication URLs:" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:4111" -ForegroundColor Green
Write-Host "Frontend UI: http://localhost:3000" -ForegroundColor Green

Write-Host "`nPort forwarding is running in background jobs." -ForegroundColor Yellow
Write-Host "To stop port forwarding, run: Get-Job | Stop-Job" -ForegroundColor Yellow
Write-Host "`nDeployment completed!" -ForegroundColor Green
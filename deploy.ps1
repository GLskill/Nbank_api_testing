# deploy.ps1
Write-Host "Deploying Nbank application..." -ForegroundColor Green

$backendFile = "infra/kube/nbank-chart/templates/bnackend.yml"
$frontendFile = "infra/kube/nbank-chart/templates/frontend.yaml"

# Применяем манифесты
kubectl apply -f $backendFile
kubectl apply -f $frontendFile

# Ждем готовности подов
Write-Host "Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=backend --timeout=60s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=60s

# Показываем статус
Write-Host "`nDeployment status:" -ForegroundColor Red
kubectl get pods
kubectl get services

Write-Host "Logs servises:" -ForegroundColor Green
kubectl logs deployment/backend --tail=20

Write-Host "`nApplication URLs:" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:30080"
Write-Host "Backend: http://localhost:30111"

Write-Host "`nBankDeployment completed!" -ForegroundColor Green

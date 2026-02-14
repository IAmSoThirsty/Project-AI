# EMERGENCY ENDPOINT TESTING SCRIPT
# Run AFTER starting the API server

Write-Host "🧪 Testing Project-AI Endpoints" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Health Check..." -ForegroundColor Yellow
curl http://localhost:8000/health
Write-Host ""

# Test 2: Submit Intent
Write-Host "2. Submitting Governance Intent..." -ForegroundColor Yellow
$intentBody = @{
    actor = "DemoUser"
    action = "access_user_data"
    payload = @{ user_id = "12345" }
} | ConvertTo-Json

curl -X POST http://localhost:8000/intent `
    -H "Content-Type: application/json" `
    -d $intentBody
Write-Host ""

# Test 3: Check Audit Log
Write-Host "3. Checking Audit Log..." -ForegroundColor Yellow
curl http://localhost:8000/audit?limit=5
Write-Host ""

# Test 4: Explainability (if available)
Write-Host "4. Querying Explainability..." -ForegroundColor Yellow
curl http://localhost:8000/explain
Write-Host ""

Write-Host "✅ Testing Complete!" -ForegroundColor Green

#                                           [2026-03-03 13:45]
#                                          Productivity: Active
# EMERGENCY DEMO SCRIPT
# Run this to start the Project-AI backend

$env:PYTHONPATH = "C:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\src"
$PYTHON = "C:\Users\Quencher\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "🌍 Starting Project-AI Governance API..." -ForegroundColor Cyan
Write-Host ""

& $PYTHON -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

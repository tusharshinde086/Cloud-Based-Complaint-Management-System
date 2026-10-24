$ErrorActionPreference = "Stop"
Write-Host "Cloud-Based Complaint Management System - setup helper" -ForegroundColor Cyan
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python and enable the Python launcher."
}
$pythonVersion = Read-Host "Enter Python launcher version (recommended 3.12; example: 3.12)"
if ([string]::IsNullOrWhiteSpace($pythonVersion)) { $pythonVersion = "3.12" }
py -$pythonVersion -m venv .venv
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Virtual environment was not created. Check that Python $pythonVersion is installed."
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env. Edit it before running the application." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists; leaving it unchanged." -ForegroundColor Yellow
}
Write-Host "Part 1 setup completed. Django application code will be added in Part 2." -ForegroundColor Green

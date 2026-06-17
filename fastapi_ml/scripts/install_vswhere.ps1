# Elevate if not running as admin
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Elevating to Administrator..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File \"$PSCommandPath\"" -Verb RunAs
    exit
}

$dest = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
$dir = Split-Path $dest -Parent
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

Write-Host "Downloading vswhere.exe to $dest"
$uri = 'https://github.com/microsoft/vswhere/releases/latest/download/vswhere.exe'
try {
    Invoke-WebRequest -Uri $uri -OutFile $dest -UseBasicParsing -ErrorAction Stop
    Write-Host "Downloaded vswhere.exe successfully."
} catch {
    Write-Error "Failed to download vswhere.exe: $_"
}

Write-Host "Done. You can now retry: pip install -r requirements.txt"
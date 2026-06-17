# Elevate if not running as admin
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Elevating to Administrator..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File \"$PSCommandPath\"" -Verb RunAs
    exit
}

$exe = "$env:TEMP\vs_BuildTools.exe"
$uri = 'https://aka.ms/vs/17/release/vs_BuildTools.exe'

Write-Host "Downloading Visual Studio Build Tools to $exe (may take a few minutes)"
try {
    Invoke-WebRequest -Uri $uri -OutFile $exe -UseBasicParsing -ErrorAction Stop
    Write-Host "Download complete. Launching installer (quiet install of C++ Build Tools)..."
    Start-Process -FilePath $exe -ArgumentList '--add Microsoft.VisualStudio.Workload.VCTools --quiet --wait --norestart --nocache' -Wait
    Write-Host "Installer finished. You may need to restart your machine."
} catch {
    Write-Error "Failed to download or run installer: $_"
}

Write-Host "After restart, activate your venv and run: pip install -r requirements.txt"
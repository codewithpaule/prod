# Setup Miniconda and create conda env with binary ML packages
# Non-elevated script. Run in PowerShell (normal user):
# powershell -ExecutionPolicy Bypass -File .\scripts\setup_conda_env.ps1

$installer = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"
$minicondaUrl = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe'
$installDir = "$env:USERPROFILE\Miniconda3"

Write-Host "Downloading Miniconda installer to $installer (if not already present)..."
if (-not (Test-Path $installer)) {
    try {
        Invoke-WebRequest -Uri $minicondaUrl -OutFile $installer -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Error "Failed to download Miniconda: $_"
        exit 1
    }
} else {
    Write-Host "Installer already exists at $installer"
}

Write-Host "Running Miniconda silent installer to $installDir"
$args = "/InstallationType=JustMe","/RegisterPython=0","/AddToPath=0","/S","/D=$installDir"
try {
    Start-Process -FilePath $installer -ArgumentList $args -Wait -NoNewWindow
} catch {
    Write-Error "Failed to run Miniconda installer: $_"
    exit 2
}

$conda = "$installDir\Scripts\conda.exe"
if (-not (Test-Path $conda)) {
    Write-Error "conda executable not found at $conda. You may need to restart your shell or run the installer manually."
    exit 3
}

Write-Host "Creating conda environment 'prod' with Python 3.11"
& $conda create -y -n prod python=3.11

Write-Host "Installing binary packages from conda-forge: pandas, numpy, scikit-learn, xgboost"
& $conda install -y -n prod -c conda-forge pandas numpy scikit-learn xgboost

# Install remaining pure-Python requirements via pip inside the conda env
$repoReqs = Join-Path (Split-Path -Parent $PSCommandPath) "..\requirements_no_pandas.txt"
$repoReqs = (Resolve-Path $repoReqs).Path
Write-Host "Using pip inside conda env to install remaining requirements from $repoReqs"
& $conda run -n prod pip install --upgrade pip setuptools wheel
& $conda run -n prod pip install -r "$repoReqs"

Write-Host "Conda environment 'prod' is ready. To use it, run:"
Write-Host "    conda activate prod"
Write-Host "Then run your project commands (uvicorn, etc.)"

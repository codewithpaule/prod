# Elevate if not running as admin
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Elevating to Administrator..."
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File \"$PSCommandPath\"" -Verb RunAs
    exit
}

$vswherePath = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path $vswherePath)) {
    Write-Host "vswhere.exe not found at $vswherePath. Downloading..."
    $uri = 'https://github.com/microsoft/vswhere/releases/latest/download/vswhere.exe'
    try {
        Invoke-WebRequest -Uri $uri -OutFile $vswherePath -UseBasicParsing -ErrorAction Stop
        Write-Host "Downloaded vswhere.exe to $vswherePath"
    } catch {
        Write-Error "Failed to download vswhere.exe: $_"
        exit 1
    }
}

Write-Host "Running: $vswherePath -products * -latest -format json"
try {
    # Invoke directly and capture stdout/stderr
    $out = & "$vswherePath" -products * -latest -format json 2>&1
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { Write-Warning "vswhere exit code: $exitCode" }
    if ([string]::IsNullOrWhiteSpace($out)) {
        Write-Warning "vswhere produced no output. Exit code: $exitCode"
        exit 2
    }
    Write-Host "--- vswhere JSON output start ---"
    Write-Host $out
    Write-Host "--- vswhere JSON output end ---"
    # try to parse JSON to check for validity
    try {
        $json = $out | ConvertFrom-Json -ErrorAction Stop
        if ($json -is [System.Array]) { $count = $json.Count } else { $count = 1 }
        Write-Host "JSON parsed successfully. Found $count entries."
    } catch {
        Write-Error "Failed to parse vswhere output as JSON: $_"
        Write-Host "Attempting to re-download vswhere.exe and retry..."
        $uri = 'https://github.com/microsoft/vswhere/releases/latest/download/vswhere.exe'
        try {
            Invoke-WebRequest -Uri $uri -OutFile $vswherePath -UseBasicParsing -ErrorAction Stop
            Write-Host "Re-downloaded vswhere.exe to $vswherePath"
            $out2 = & "$vswherePath" -products * -latest -format json 2>&1
            Write-Host "--- vswhere JSON output (after re-download) ---"
            Write-Host $out2
        } catch {
            Write-Error "Retry failed: $_"
            exit 3
        }
    }
} catch {
    Write-Error "Error running vswhere.exe: $_"
    exit 4
}

Write-Host "Done. If output parsed successfully, retry: pip install -r requirements.txt"
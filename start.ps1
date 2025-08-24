param(
    [ValidateSet('default','development','sqlite')]
    [string]$Config = 'default',
    [switch]$Background,
    [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Gå till repo-roten
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

# Skapa venv om den saknas
$venvDir = Join-Path $Here '.venv'
$activate = Join-Path $venvDir 'Scripts/Activate.ps1'
if (-not (Test-Path $activate)) {
    Write-Host 'Skapar virtuell miljö (.venv)...' -ForegroundColor Cyan
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 -m venv $venvDir
    } else {
        python -m venv $venvDir
    }
}

# Aktivera venv
. $activate

# Installera beroenden (om inte hoppat över)
if (-not $SkipInstall) {
    if (Test-Path (Join-Path $Here 'requirements.txt')) {
        Write-Host 'Uppgraderar pip och installerar beroenden...' -ForegroundColor Cyan
        python -m pip install --upgrade pip
        python -m pip install -r (Join-Path $Here 'requirements.txt')
    }
} else {
    Write-Host 'Skippar installation av beroenden (-SkipInstall).' -ForegroundColor Yellow
}

# Kontrollera ODBC-drivrutin (för MSSQL via pyodbc)
try {
    $odbcKey = 'HKLM:\SOFTWARE\ODBC\ODBCINST.INI\ODBC Drivers'
    $drivers = (Get-ItemProperty $odbcKey).PSObject.Properties | ForEach-Object { $_.Name }
} catch { $drivers = @() }

if (-not ($drivers -contains 'ODBC Driver 17 for SQL Server' -or $drivers -contains 'ODBC Driver 18 for SQL Server')) {
    Write-Warning 'Ingen ODBC Driver 17/18 for SQL Server hittades. Installera från Microsoft om SQL Server-anslutning krävs.'
}

# Konfiguration
$env:FLASK_CONFIG = $Config
Write-Host "Startar appen med FLASK_CONFIG=$Config ..." -ForegroundColor Green

if ($Background) {
    # Starta i separat PowerShell-process så att denna terminal släpps direkt
    $psCmd = @"
Set-Location '$Here'
. '$activate'
`$env:FLASK_CONFIG = '$Config'
python run.py
"@
    Start-Process -FilePath "powershell.exe" -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-Command', $psCmd) | Out-Null
    Write-Host 'Servern startades i bakgrunden (separat PowerShell-fönster).' -ForegroundColor Green
} else {
    # Kör i aktuell terminal (blockerar tills du stoppar den)
    python run.py
}

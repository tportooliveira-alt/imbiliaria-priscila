# dev.ps1 — boot único do site (Priscila Vasconcelos Imóveis)
# Uso:  .\dev.ps1            -> sobe servidor + abre navegador
#       .\dev.ps1 -NoBrowser  -> só sobe servidor
#       .\dev.ps1 -Test       -> roda pytest e sai

param(
    [switch]$NoBrowser,
    [switch]$Test,
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# 1. venv
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[dev.ps1] criando venv..." -ForegroundColor Yellow
    python -m venv venv
}
& ".\venv\Scripts\Activate.ps1"

# 2. dependências (rápido, só se faltar marker)
$marker = ".\venv\.deps_ok"
if (-not (Test-Path $marker) -or (Get-Item requirements.txt).LastWriteTime -gt (Get-Item $marker).LastWriteTime) {
    Write-Host "[dev.ps1] instalando requirements..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
    New-Item -ItemType File -Path $marker -Force | Out-Null
}

# 3. .env
if (-not (Test-Path ".\.env")) {
    Write-Host "[dev.ps1] criando .env a partir do .env.exemplo..." -ForegroundColor Yellow
    Copy-Item .env.exemplo .env
}

# 4. testes rápidos opcional
if ($Test) {
    pytest -q
    exit $LASTEXITCODE
}

# 5. derruba processo travado na porta
$busy = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($busy) {
    $pids = $busy.OwningProcess | Select-Object -Unique
    Write-Host "[dev.ps1] porta $Port ocupada — finalizando PID $($pids -join ',')" -ForegroundColor Yellow
    foreach ($processId in $pids) { Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Milliseconds 600
}

# 6. abre navegador depois de 1.5s
if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($p)
        Start-Sleep -Seconds 2
        $url = "http://localhost:$p/v3-editorial/"
        $chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        if (Test-Path $chrome) {
            Start-Process -FilePath $chrome -ArgumentList $url
        } else {
            Start-Process $url
        }
    } -ArgumentList $Port | Out-Null
}

# 7. servidor
Write-Host "[dev.ps1] uvicorn em http://localhost:$Port" -ForegroundColor Green
uvicorn server:app --host 127.0.0.1 --port $Port --reload --reload-exclude "data/*" --reload-exclude "assets/imoveis/*" --reload-exclude "logs/*"

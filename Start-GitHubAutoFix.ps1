$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Data = Join-Path $Root 'data'
New-Item -ItemType Directory -Force -Path $Data | Out-Null

if (-not $env:GH_TOKEN) {
    $TokenPath = Join-Path $Data 'token.dpapi'
    if (Test-Path $TokenPath) {
        $SecureToken = Get-Content -Raw $TokenPath | ConvertTo-SecureString
    } else {
        $SecureToken = Read-Host 'Token GitHub classic da conta brunnojob' -AsSecureString
    }
    $Pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureToken)
    try {
        $env:GH_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Pointer)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Pointer)
    }
}

try {
    $Python = Get-Command python -ErrorAction Stop
    $ScriptPath = Join-Path $Root 'github_autofix.py'
    $LogPath = Join-Path $Data 'monitor.log'
    & $Python.Source -u $ScriptPath --apply --data-dir $Data *>> $LogPath
    $MonitorExit = $LASTEXITCODE
} finally {
    Remove-Item Env:GH_TOKEN -ErrorAction SilentlyContinue
}
exit $MonitorExit

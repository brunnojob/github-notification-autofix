$ErrorActionPreference = 'Stop'
Get-Command git -ErrorAction Stop | Out-Null
Get-Command python -ErrorAction Stop | Out-Null
Get-Command codex -ErrorAction Stop | Out-Null
& codex login status
if ($LASTEXITCODE -ne 0) {
    throw 'Execute codex login e depois rode este instalador novamente.'
}

$Root = $PSScriptRoot
$Data = Join-Path $Root 'data'
New-Item -ItemType Directory -Force -Path $Data | Out-Null
$SecureToken = Read-Host 'Token GitHub classic de brunnojob (notifications, repo e workflow)' -AsSecureString
$TokenPath = Join-Path $Data 'token.dpapi'
$SecureToken | ConvertFrom-SecureString | Set-Content -Encoding UTF8 $TokenPath

$Pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureToken)
try {
    $env:GH_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Pointer)
    & python (Join-Path $Root 'github_autofix.py') --check-setup --data-dir $Data
    if ($LASTEXITCODE -ne 0) {
        throw 'A verificação inicial encontrou um bloqueio. Consulte a saída antes de instalar a tarefa.'
    }
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Pointer)
    Remove-Item Env:GH_TOKEN -ErrorAction SilentlyContinue
}

$Launcher = Join-Path $Root 'Start-GitHubAutoFix.ps1'
Unblock-File $Launcher
$PowerShell = (Get-Command powershell.exe).Source
$Arguments = '-NoProfile -WindowStyle Hidden -ExecutionPolicy RemoteSigned -File "' + $Launcher + '"'
$Action = New-ScheduledTaskAction -Execute $PowerShell -Argument $Arguments -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew
$CurrentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited
$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal
Register-ScheduledTask -TaskName 'BrunnoJob-GitHub-AutoFix' -InputObject $Task -Force | Out-Null
Start-ScheduledTask -TaskName 'BrunnoJob-GitHub-AutoFix'
Write-Host 'Monitor iniciado. Reinicia ao entrar no Windows. Logs em data\monitor.log.'

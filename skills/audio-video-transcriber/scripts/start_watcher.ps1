$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = if ($env:AVT_BASE_DIR) { $env:AVT_BASE_DIR } else { Join-Path $env:USERPROFILE "AudioVideoTranscriber" }
$VenvDir = if ($env:AVT_VENV_DIR) { $env:AVT_VENV_DIR } else { Join-Path $env:USERPROFILE ".audio-video-transcriber\venv" }
$PidFile = Join-Path $BaseDir "logs\watcher.pid"
$OutLog = Join-Path $BaseDir "logs\watcher.out.log"
$ErrLog = Join-Path $BaseDir "logs\watcher.err.log"

function Get-PythonPath {
    if ($env:AVT_PYTHON_BIN -and (Test-Path $env:AVT_PYTHON_BIN)) { return $env:AVT_PYTHON_BIN }
    $venvPython = Join-Path $VenvDir "Scripts\python.exe"
    if (Test-Path $venvPython) { return $venvPython }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) { return $python3.Source }
    return $null
}

New-Item -ItemType Directory -Force -Path `
    (Join-Path $BaseDir "inbox"), `
    (Join-Path $BaseDir "output"), `
    (Join-Path $BaseDir "done"), `
    (Join-Path $BaseDir "logs") | Out-Null

if (Test-Path $PidFile) {
    $OldPid = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($OldPid) {
        $Existing = Get-Process -Id ([int]$OldPid) -ErrorAction SilentlyContinue
        if ($Existing) {
            Write-Host "Watcher is already running with PID $OldPid."
            Write-Host "Inbox:  $(Join-Path $BaseDir "inbox")"
            Write-Host "Output: $(Join-Path $BaseDir "output")"
            Write-Host "Done:   $(Join-Path $BaseDir "done")"
            Write-Host "Logs:   $(Join-Path $BaseDir "logs")"
            exit 0
        }
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

$PythonPath = Get-PythonPath
if (-not $PythonPath) {
    Write-Error "Python was not found. Please install Python 3 first."
    exit 1
}

try {
    & $PythonPath -c "import watchdog" | Out-Null
} catch {
    Write-Host "watchdog is not installed for:"
    Write-Host "  $PythonPath"
    Write-Host ""
    Write-Host "Run:"
    Write-Host "  .\skills\audio-video-transcriber\scripts\install_whisper.ps1"
    exit 1
}

$Process = Start-Process -FilePath $PythonPath `
    -ArgumentList @((Join-Path $ScriptDir "watch_inbox.py")) `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path $PidFile -Value $Process.Id

Write-Host "Started watcher with PID $($Process.Id)."
Write-Host "Inbox:  $(Join-Path $BaseDir "inbox")"
Write-Host "Output: $(Join-Path $BaseDir "output")"
Write-Host "Done:   $(Join-Path $BaseDir "done")"
Write-Host "Logs:   $(Join-Path $BaseDir "logs")"

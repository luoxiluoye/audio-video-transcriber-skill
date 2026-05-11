$ErrorActionPreference = "Stop"

$BaseDir = if ($env:AVT_BASE_DIR) { $env:AVT_BASE_DIR } else { Join-Path $env:USERPROFILE "AudioVideoTranscriber" }
$VenvDir = if ($env:AVT_VENV_DIR) { $env:AVT_VENV_DIR } else { Join-Path $env:USERPROFILE ".audio-video-transcriber\venv" }
$PidFile = Join-Path $BaseDir "logs\watcher.pid"

function Get-PythonPath {
    if ($env:AVT_PYTHON_BIN -and (Test-Path $env:AVT_PYTHON_BIN)) { return $env:AVT_PYTHON_BIN }
    $venvPython = Join-Path $VenvDir "Scripts\python.exe"
    if (Test-Path $venvPython) { return $venvPython }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) { return $python3.Source }
    return "not found"
}

function Get-WhisperPath {
    if ($env:AVT_WHISPER_BIN -and (Test-Path $env:AVT_WHISPER_BIN)) { return $env:AVT_WHISPER_BIN }
    $whisper = Get-Command whisper -ErrorAction SilentlyContinue
    if ($whisper) { return $whisper.Source }
    $venvWhisper = Join-Path $VenvDir "Scripts\whisper.exe"
    if (Test-Path $venvWhisper) { return $venvWhisper }
    return "not found"
}

function Write-LogTail {
    param([string]$Path)
    Write-Host ""
    Write-Host "Last 20 lines: $Path"
    if (Test-Path $Path) {
        Get-Content $Path -Tail 20
    } else {
        Write-Host "  No log file yet."
    }
}

New-Item -ItemType Directory -Force -Path `
    (Join-Path $BaseDir "inbox"), `
    (Join-Path $BaseDir "output"), `
    (Join-Path $BaseDir "done"), `
    (Join-Path $BaseDir "logs") | Out-Null

Write-Host "Audio Video Transcriber status"
Write-Host ""
Write-Host "Base dir: $BaseDir"
Write-Host "Inbox:    $(Join-Path $BaseDir "inbox")"
Write-Host "Output:   $(Join-Path $BaseDir "output")"
Write-Host "Done:     $(Join-Path $BaseDir "done")"
Write-Host "Logs:     $(Join-Path $BaseDir "logs")"
Write-Host ""

if (Test-Path $PidFile) {
    $PidValue = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    $Process = if ($PidValue) { Get-Process -Id ([int]$PidValue) -ErrorAction SilentlyContinue } else { $null }
    if ($Process) {
        Write-Host "Watcher:  running (PID $PidValue)"
    } else {
        Write-Host "Watcher:  not running (stale PID file)"
    }
} else {
    Write-Host "Watcher:  not running"
}

Write-Host "Whisper:  $(Get-WhisperPath)"
Write-Host "Python:   $(Get-PythonPath)"

Write-LogTail (Join-Path $BaseDir "logs\transcriber.log")
Write-LogTail (Join-Path $BaseDir "logs\watcher.out.log")
Write-LogTail (Join-Path $BaseDir "logs\watcher.err.log")

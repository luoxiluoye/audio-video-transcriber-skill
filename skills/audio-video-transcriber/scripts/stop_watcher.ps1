$ErrorActionPreference = "Stop"

$BaseDir = if ($env:AVT_BASE_DIR) { $env:AVT_BASE_DIR } else { Join-Path $env:USERPROFILE "AudioVideoTranscriber" }
$PidFile = Join-Path $BaseDir "logs\watcher.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "Watcher is not running. No PID file found."
    exit 0
}

$PidValue = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
if (-not $PidValue) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Watcher is not running. Removed empty PID file."
    exit 0
}

$Process = Get-Process -Id ([int]$PidValue) -ErrorAction SilentlyContinue
if ($Process) {
    Write-Host "Stopping watcher with PID $PidValue..."
    Stop-Process -Id ([int]$PidValue) -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    $StillRunning = Get-Process -Id ([int]$PidValue) -ErrorAction SilentlyContinue
    if ($StillRunning) {
        Write-Host "Watcher is still shutting down. Check status in a moment."
    } else {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "Watcher stopped."
    }
} else {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Watcher is not running. Removed stale PID file."
}

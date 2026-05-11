param(
    [switch]$Yes
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = if ($env:AVT_BASE_DIR) { $env:AVT_BASE_DIR } else { Join-Path $env:USERPROFILE "AudioVideoTranscriber" }
$VenvDir = if ($env:AVT_VENV_DIR) { $env:AVT_VENV_DIR } else { Join-Path $env:USERPROFILE ".audio-video-transcriber\venv" }

New-Item -ItemType Directory -Force -Path `
    (Join-Path $BaseDir "inbox"), `
    (Join-Path $BaseDir "output"), `
    (Join-Path $BaseDir "done"), `
    (Join-Path $BaseDir "logs") | Out-Null

Write-Host "Created local working directories:"
Write-Host "  $(Join-Path $BaseDir "inbox")"
Write-Host "  $(Join-Path $BaseDir "output")"
Write-Host "  $(Join-Path $BaseDir "done")"
Write-Host "  $(Join-Path $BaseDir "logs")"
Write-Host ""

& (Join-Path $ScriptDir "doctor.ps1")
Write-Host ""

$WhisperFound = $false
if ($env:AVT_WHISPER_BIN -and (Test-Path $env:AVT_WHISPER_BIN)) {
    $WhisperFound = $true
} elseif (Get-Command whisper -ErrorAction SilentlyContinue) {
    $WhisperFound = $true
} elseif (Test-Path (Join-Path $VenvDir "Scripts\whisper.exe")) {
    $WhisperFound = $true
}

if (-not $WhisperFound) {
    if ($Yes) {
        Write-Host "Installing local Python Whisper environment..."
        & (Join-Path $ScriptDir "install_whisper.ps1")
    } else {
        Write-Host "Whisper CLI not found."
        Write-Host "To install a local Python environment, run:"
        Write-Host "  .\skills\audio-video-transcriber\scripts\install_whisper.ps1"
        Write-Host ""
        Write-Host "Or run one-step initialization:"
        Write-Host "  .\skills\audio-video-transcriber\scripts\bootstrap.ps1 -Yes"
    }
} else {
    Write-Host "Whisper CLI is available. You can start transcribing."
}

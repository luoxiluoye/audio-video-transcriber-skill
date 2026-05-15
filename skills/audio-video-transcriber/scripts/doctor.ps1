$ErrorActionPreference = "Stop"

$DefaultBaseDir = Join-Path $env:USERPROFILE "AudioVideoTranscriber"
$DefaultVenvDir = Join-Path $env:USERPROFILE ".audio-video-transcriber\venv"
$BaseDir = if ($env:AVT_BASE_DIR) { $env:AVT_BASE_DIR } else { $DefaultBaseDir }
$VenvDir = if ($env:AVT_VENV_DIR) { $env:AVT_VENV_DIR } else { $DefaultVenvDir }

function Get-CommandPath {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Get-PythonPath {
    if ($env:AVT_PYTHON_BIN -and (Test-Path $env:AVT_PYTHON_BIN)) { return $env:AVT_PYTHON_BIN }
    $python = Get-CommandPath "python"
    if ($python) { return $python }
    $python3 = Get-CommandPath "python3"
    if ($python3) { return $python3 }
    return $null
}

function Get-WhisperPath {
    if ($env:AVT_WHISPER_BIN -and (Test-Path $env:AVT_WHISPER_BIN)) { return $env:AVT_WHISPER_BIN }
    $whisper = Get-CommandPath "whisper"
    if ($whisper) { return $whisper }
    $venvWhisper = Join-Path $VenvDir "Scripts\whisper.exe"
    if (Test-Path $venvWhisper) { return $venvWhisper }
    return $null
}

function Write-Check {
    param([string]$Label, [string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { $Value = "not found" }
    "{0,-18} {1}" -f "${Label}:", $Value
}

$PythonPath = Get-PythonPath
$WhisperPath = Get-WhisperPath
$FfmpegPath = Get-CommandPath "ffmpeg"
$PipStatus = ""
$WatchdogStatus = ""
$PythonDocxStatus = ""

if ($PythonPath) {
    try { $PipStatus = (& $PythonPath -m pip --version 2>$null) -join "`n" } catch { $PipStatus = "" }
    try { $WatchdogStatus = (& $PythonPath -c "import watchdog; print('installed')" 2>$null) -join "`n" } catch { $WatchdogStatus = "" }
    try { $PythonDocxStatus = (& $PythonPath -c "import docx; print('installed')" 2>$null) -join "`n" } catch { $PythonDocxStatus = "" }
}

Write-Host "Audio Video Transcriber doctor"
Write-Host ""
Write-Check "system" "Windows native PowerShell"
Write-Check "python" $PythonPath
Write-Check "pip" $PipStatus
Write-Check "whisper CLI" $WhisperPath
Write-Check "ffmpeg" $FfmpegPath
Write-Check "watchdog" $WatchdogStatus
Write-Check "python-docx" $PythonDocxStatus
Write-Host ""
Write-Host "Environment:"
"{0,-18} {1}" -f "AVT_WHISPER_BIN:", $(if ($env:AVT_WHISPER_BIN) { $env:AVT_WHISPER_BIN } else { "not set" })
"{0,-18} {1}" -f "AVT_PYTHON_BIN:", $(if ($env:AVT_PYTHON_BIN) { $env:AVT_PYTHON_BIN } else { "not set" })
"{0,-18} {1}" -f "AVT_BASE_DIR:", $BaseDir
"{0,-18} {1}" -f "AVT_VENV_DIR:", $VenvDir
Write-Host ""

if (-not $WhisperPath) {
    Write-Host "Whisper CLI not found."
    Write-Host "Run:"
    Write-Host "  .\skills\audio-video-transcriber\scripts\install_whisper.ps1"
    Write-Host ""
}

if (-not $FfmpegPath) {
    Write-Host "ffmpeg not found."
    Write-Host "Please install ffmpeg and add it to PATH."
    Write-Host ""
}

Write-Host "Recommended next step:"
if (-not $PythonPath) {
    Write-Host "  Install Python 3, then run this doctor again."
} elseif (-not $WhisperPath) {
    Write-Host "  .\skills\audio-video-transcriber\scripts\install_whisper.ps1"
} elseif ((-not $WatchdogStatus) -or (-not $PythonDocxStatus)) {
    Write-Host "  .\skills\audio-video-transcriber\scripts\install_whisper.ps1"
} else {
    Write-Host "  .\skills\audio-video-transcriber\scripts\status.ps1"
}

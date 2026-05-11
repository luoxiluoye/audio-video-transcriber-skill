$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = if ($env:AVT_VENV_DIR) { $env:AVT_VENV_DIR } else { Join-Path $env:USERPROFILE ".audio-video-transcriber\venv" }
$BaseDir = if ($env:AVT_BASE_DIR) { $env:AVT_BASE_DIR } else { Join-Path $env:USERPROFILE "AudioVideoTranscriber" }
$Model = if ($env:AVT_MODEL) { $env:AVT_MODEL } else { "small" }
$Language = if ($env:AVT_LANGUAGE) { $env:AVT_LANGUAGE } else { "Chinese" }

function Get-PythonPath {
    if ($env:AVT_PYTHON_BIN -and (Test-Path $env:AVT_PYTHON_BIN)) { return $env:AVT_PYTHON_BIN }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) { return $python3.Source }
    return $null
}

$PythonPath = Get-PythonPath
if (-not $PythonPath) {
    Write-Error "Python was not found. Please install Python 3 and run this script again."
    exit 1
}

Write-Host "Creating local virtual environment:"
Write-Host "  $VenvDir"
& $PythonPath -m venv $VenvDir

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment Python was not found at: $VenvPython"
    exit 1
}

Write-Host "Installing Python packages: openai-whisper and watchdog"
& $VenvPython -m pip install -U pip setuptools wheel
& $VenvPython -m pip install -U openai-whisper watchdog

New-Item -ItemType Directory -Force -Path `
    (Join-Path $BaseDir "inbox"), `
    (Join-Path $BaseDir "output"), `
    (Join-Path $BaseDir "done"), `
    (Join-Path $BaseDir "logs") | Out-Null

Write-Host ""
Write-Host "Installation complete."
Write-Host ""
Write-Host "Optional PowerShell environment settings for this session:"
Write-Host "  `$env:AVT_PYTHON_BIN = `"$VenvDir\Scripts\python.exe`""
Write-Host "  `$env:AVT_WHISPER_BIN = `"$VenvDir\Scripts\whisper.exe`""
Write-Host "  `$env:AVT_BASE_DIR = `"$BaseDir`""
Write-Host "  `$env:AVT_MODEL = `"$Model`""
Write-Host "  `$env:AVT_LANGUAGE = `"$Language`""
Write-Host ""

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "ffmpeg was not found."
    Write-Host "Please install ffmpeg and add it to PATH."
    Write-Host ""
}

$env:AVT_PYTHON_BIN = $VenvPython
$env:AVT_WHISPER_BIN = Join-Path $VenvDir "Scripts\whisper.exe"
$env:AVT_BASE_DIR = $BaseDir
$env:AVT_MODEL = $Model
$env:AVT_LANGUAGE = $Language
& (Join-Path $ScriptDir "doctor.ps1")

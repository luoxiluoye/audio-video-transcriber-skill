param(
    [Parameter(Position = 0)]
    [string]$Command,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$ScriptDir = Join-Path $RootDir "skills/audio-video-transcriber/scripts"

function Show-Help {
    @"
Audio Video Transcriber Toolkit

Usage:
  .\bin\avt.ps1 doctor
  .\bin\avt.ps1 install
  .\bin\avt.ps1 bootstrap
  .\bin\avt.ps1 transcribe "C:\path\to\file.mp4" [transcribe options]
  .\bin\avt.ps1 review "C:\path\to\transcript.txt"
  .\bin\avt.ps1 watch
  .\bin\avt.ps1 stop
  .\bin\avt.ps1 status
  .\bin\avt.ps1 help

Examples:
  .\bin\avt.ps1 doctor
  .\bin\avt.ps1 bootstrap
  .\bin\avt.ps1 transcribe "$env:USERPROFILE\Desktop\test.mp4"
  .\bin\avt.ps1 transcribe "$env:USERPROFILE\Desktop\test.mp4" --model medium --language auto
  .\bin\avt.ps1 review "$env:USERPROFILE\AudioVideoTranscriber\output\test.txt"
  .\bin\avt.ps1 watch
  .\bin\avt.ps1 stop
  .\bin\avt.ps1 status
"@
}

if ([string]::IsNullOrWhiteSpace($Command)) {
    Show-Help
    exit 1
}

switch ($Command.ToLowerInvariant()) {
    "--help" { Show-Help }
    "-h" { Show-Help }
    "help" { Show-Help }
    "doctor" { & (Join-Path $ScriptDir "doctor.ps1") @RemainingArgs }
    "install" { & (Join-Path $ScriptDir "install_whisper.ps1") @RemainingArgs }
    "bootstrap" { & (Join-Path $ScriptDir "bootstrap.ps1") -Yes @RemainingArgs }
    "transcribe" {
        if ($RemainingArgs.Count -lt 1) {
            Write-Error "Missing input file. Example: .\bin\avt.ps1 transcribe `"C:\path\to\file.mp4`""
            exit 1
        }
        $python = if ($env:AVT_PYTHON_BIN) { $env:AVT_PYTHON_BIN } else { "python" }
        & $python (Join-Path $ScriptDir "transcribe.py") @RemainingArgs
    }
    "review" {
        if ($RemainingArgs.Count -lt 1) {
            Write-Error "Missing transcript file. Example: .\bin\avt.ps1 review `"$env:USERPROFILE\AudioVideoTranscriber\output\test.txt`""
            exit 1
        }
        $python = if ($env:AVT_PYTHON_BIN) { $env:AVT_PYTHON_BIN } else { "python" }
        & $python (Join-Path $ScriptDir "postprocess.py") @RemainingArgs
    }
    "watch" { & (Join-Path $ScriptDir "start_watcher.ps1") @RemainingArgs }
    "stop" { & (Join-Path $ScriptDir "stop_watcher.ps1") @RemainingArgs }
    "status" { & (Join-Path $ScriptDir "status.ps1") @RemainingArgs }
    default {
        Write-Host "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}

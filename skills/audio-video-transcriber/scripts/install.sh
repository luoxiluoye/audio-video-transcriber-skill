#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
PYTHON_BIN="${AVT_PYTHON_BIN:-}"

mkdir -p "$AVT_BASE_DIR/inbox" "$AVT_BASE_DIR/output" "$AVT_BASE_DIR/done" "$AVT_BASE_DIR/logs"

echo "Created local working directories:"
echo "  $AVT_BASE_DIR/inbox"
echo "  $AVT_BASE_DIR/output"
echo "  $AVT_BASE_DIR/done"
echo "  $AVT_BASE_DIR/logs"
echo

if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  else
    echo "Python 3 was not found. Please install Python 3 first."
    exit 1
  fi
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python is not executable: $PYTHON_BIN"
  exit 1
fi

echo "Using Python:"
echo "  $PYTHON_BIN"

if command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg found:"
  echo "  $(command -v ffmpeg)"
else
  echo "ffmpeg was not found. Whisper needs ffmpeg for most audio/video formats."
  case "$(uname -s 2>/dev/null || true)" in
    Darwin) echo "Install with: brew install ffmpeg" ;;
    Linux) echo "Install with: sudo apt update && sudo apt install -y ffmpeg" ;;
    *) echo "Please install ffmpeg and add it to PATH." ;;
  esac
fi

WHISPER_PATH=""
if [ -n "${AVT_WHISPER_BIN:-}" ] && [ -x "${AVT_WHISPER_BIN:-}" ]; then
  WHISPER_PATH="$AVT_WHISPER_BIN"
elif command -v whisper >/dev/null 2>&1; then
  WHISPER_PATH="$(command -v whisper)"
elif [ -x "${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/whisper" ]; then
  WHISPER_PATH="${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/whisper"
fi

if [ -n "$WHISPER_PATH" ]; then
  echo "Whisper CLI found:"
  echo "  $WHISPER_PATH"
else
  echo "Whisper CLI was not found."
  echo "To install it locally, run:"
  echo "  $SCRIPT_DIR/install_whisper.sh"
  echo "or:"
  echo "  $SCRIPT_DIR/bootstrap.sh --yes"
fi

echo
echo "Installing watchdog for the inbox watcher and python-docx for Word review files."
if [ -n "${AVT_PYTHON_BIN:-}" ]; then
  "$PYTHON_BIN" -m pip install -U watchdog python-docx
else
  "$PYTHON_BIN" -m pip install --user -U watchdog python-docx
fi

echo
echo "Next steps:"
echo "  Check status:     $SCRIPT_DIR/status.sh"
echo "  Transcribe file:  python3 skills/audio-video-transcriber/scripts/transcribe.py /path/to/file.mp4"
echo "  Start watcher:    $SCRIPT_DIR/start_watcher.sh"

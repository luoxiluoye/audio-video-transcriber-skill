#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_VENV_DIR="${HOME}/.audio-video-transcriber/venv"
AVT_VENV_DIR_VALUE="${AVT_VENV_DIR:-$DEFAULT_VENV_DIR}"
PYTHON_CANDIDATE="${AVT_PYTHON_BIN:-}"

detect_os() {
  local uname_s
  uname_s="$(uname -s 2>/dev/null || true)"
  case "$uname_s" in
    Darwin) echo "macOS" ;;
    Linux)
      if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "WSL"
      else
        echo "Linux"
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*) echo "Windows Git Bash" ;;
    *) echo "Unknown" ;;
  esac
}

find_python() {
  if [ -n "$PYTHON_CANDIDATE" ] && [ -x "$PYTHON_CANDIDATE" ]; then
    echo "$PYTHON_CANDIDATE"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  return 1
}

find_whisper() {
  if [ -n "${AVT_WHISPER_BIN:-}" ] && [ -x "${AVT_WHISPER_BIN:-}" ]; then
    echo "$AVT_WHISPER_BIN"
    return 0
  fi
  if command -v whisper >/dev/null 2>&1; then
    command -v whisper
    return 0
  fi
  if [ -x "$AVT_VENV_DIR_VALUE/bin/whisper" ]; then
    echo "$AVT_VENV_DIR_VALUE/bin/whisper"
    return 0
  fi
  return 1
}

print_check() {
  local label="$1"
  local value="$2"
  if [ -n "$value" ]; then
    printf "  %-18s %s\n" "$label:" "$value"
  else
    printf "  %-18s %s\n" "$label:" "not found"
  fi
}

OS_NAME="$(detect_os)"
PYTHON_PATH="$(find_python || true)"
WHISPER_PATH="$(find_whisper || true)"

if [ -n "$PYTHON_PATH" ]; then
  PIP_PATH="$("$PYTHON_PATH" -m pip --version 2>/dev/null || true)"
  WATCHDOG_STATUS="$("$PYTHON_PATH" -c 'import watchdog; print("installed")' 2>/dev/null || true)"
else
  PIP_PATH=""
  WATCHDOG_STATUS=""
fi

FFMPEG_PATH="$(command -v ffmpeg 2>/dev/null || true)"

echo "Audio Video Transcriber doctor"
echo
print_check "system" "$OS_NAME"
print_check "python3" "$PYTHON_PATH"
print_check "pip" "$PIP_PATH"
print_check "whisper CLI" "$WHISPER_PATH"
print_check "ffmpeg" "$FFMPEG_PATH"
print_check "watchdog" "$WATCHDOG_STATUS"
echo
echo "Environment:"
printf "  %-18s %s\n" "AVT_WHISPER_BIN:" "${AVT_WHISPER_BIN:-not set}"
printf "  %-18s %s\n" "AVT_PYTHON_BIN:" "${AVT_PYTHON_BIN:-not set}"
printf "  %-18s %s\n" "AVT_BASE_DIR:" "${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
printf "  %-18s %s\n" "AVT_VENV_DIR:" "${AVT_VENV_DIR:-$DEFAULT_VENV_DIR}"
echo

if [ -z "$WHISPER_PATH" ]; then
  echo "Whisper CLI not found."
  echo "Run:"
  echo "  ./skills/audio-video-transcriber/scripts/install_whisper.sh"
  echo
fi

if [ -z "$FFMPEG_PATH" ]; then
  echo "ffmpeg not found."
  case "$OS_NAME" in
    macOS)
      echo "Install with:"
      echo "  brew install ffmpeg"
      ;;
    Linux|WSL)
      echo "Install with:"
      echo "  sudo apt update && sudo apt install -y ffmpeg"
      ;;
    Windows\ Git\ Bash)
      echo "Please install ffmpeg and add it to PATH."
      ;;
    *)
      echo "Please install ffmpeg for your system and add it to PATH."
      ;;
  esac
  echo
fi

echo "Recommended next step:"
if [ -z "$PYTHON_PATH" ]; then
  echo "  Install Python 3, then run this doctor again."
elif [ -z "$WHISPER_PATH" ]; then
  echo "  $SCRIPT_DIR/install_whisper.sh"
elif [ -z "$WATCHDOG_STATUS" ]; then
  echo "  $SCRIPT_DIR/install.sh"
else
  echo "  $SCRIPT_DIR/status.sh"
fi

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AVT_VENV_DIR="${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}"
AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
AVT_MODEL="${AVT_MODEL:-small}"
AVT_LANGUAGE="${AVT_LANGUAGE:-Chinese}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found."
  echo "Please install Python 3 and run this script again."
  exit 1
fi

echo "Creating local virtual environment:"
echo "  $AVT_VENV_DIR"
python3 -m venv "$AVT_VENV_DIR"

# shellcheck disable=SC1091
source "$AVT_VENV_DIR/bin/activate"

echo "Installing Python packages: openai-whisper, watchdog, and python-docx"
python -m pip install -U pip setuptools wheel
python -m pip install -U openai-whisper watchdog python-docx

mkdir -p "$AVT_BASE_DIR/inbox" "$AVT_BASE_DIR/output" "$AVT_BASE_DIR/done" "$AVT_BASE_DIR/logs"

echo
echo "Installation complete."
echo
echo "Optional shell environment settings:"
echo "  export AVT_PYTHON_BIN=\"$AVT_VENV_DIR/bin/python\""
echo "  export AVT_WHISPER_BIN=\"$AVT_VENV_DIR/bin/whisper\""
echo "  export AVT_BASE_DIR=\"$AVT_BASE_DIR\""
echo "  export AVT_MODEL=\"$AVT_MODEL\""
echo "  export AVT_LANGUAGE=\"$AVT_LANGUAGE\""
echo

if ! command -v ffmpeg >/dev/null 2>&1; then
  case "$(uname -s 2>/dev/null || true)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        echo "ffmpeg was not found. Install it with:"
        echo "  brew install ffmpeg"
      else
        echo "ffmpeg was not found. Install ffmpeg for macOS and add it to PATH."
      fi
      ;;
    Linux)
      echo "ffmpeg was not found. On Ubuntu/Debian, install it with:"
      echo "  sudo apt update && sudo apt install -y ffmpeg"
      ;;
    *)
      echo "ffmpeg was not found. Please install ffmpeg and add it to PATH."
      ;;
  esac
  echo
fi

export AVT_PYTHON_BIN="$AVT_VENV_DIR/bin/python"
export AVT_WHISPER_BIN="$AVT_VENV_DIR/bin/whisper"
export AVT_BASE_DIR
export AVT_MODEL
export AVT_LANGUAGE
"$SCRIPT_DIR/doctor.sh"

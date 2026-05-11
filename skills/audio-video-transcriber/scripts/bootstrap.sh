#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
YES="false"

for arg in "$@"; do
  case "$arg" in
    --yes|-y) YES="true" ;;
    *)
      echo "Unknown option: $arg"
      echo "Usage: $0 [--yes]"
      exit 1
      ;;
  esac
done

mkdir -p "$AVT_BASE_DIR/inbox" "$AVT_BASE_DIR/output" "$AVT_BASE_DIR/done" "$AVT_BASE_DIR/logs"

echo "Created local working directories:"
echo "  $AVT_BASE_DIR/inbox"
echo "  $AVT_BASE_DIR/output"
echo "  $AVT_BASE_DIR/done"
echo "  $AVT_BASE_DIR/logs"
echo

"$SCRIPT_DIR/doctor.sh"
echo

WHISPER_FOUND="false"
if [ -n "${AVT_WHISPER_BIN:-}" ] && [ -x "${AVT_WHISPER_BIN:-}" ]; then
  WHISPER_FOUND="true"
elif command -v whisper >/dev/null 2>&1; then
  WHISPER_FOUND="true"
elif [ -x "${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/whisper" ]; then
  WHISPER_FOUND="true"
fi

if [ "$WHISPER_FOUND" = "false" ]; then
  if [ "$YES" = "true" ]; then
    echo "Installing local Python Whisper environment..."
    "$SCRIPT_DIR/install_whisper.sh"
  else
    echo "Whisper CLI not found."
    echo "To install a local Python environment, run:"
    echo "  $SCRIPT_DIR/install_whisper.sh"
    echo
    echo "Or run one-step initialization:"
    echo "  $SCRIPT_DIR/bootstrap.sh --yes"
  fi
else
  echo "Whisper CLI is available. You can start transcribing."
fi

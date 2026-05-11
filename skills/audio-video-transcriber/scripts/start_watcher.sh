#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
VENV_PYTHON="${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/python"
PID_FILE="$AVT_BASE_DIR/logs/watcher.pid"
OUT_LOG="$AVT_BASE_DIR/logs/watcher.out.log"
ERR_LOG="$AVT_BASE_DIR/logs/watcher.err.log"

mkdir -p "$AVT_BASE_DIR/inbox" "$AVT_BASE_DIR/output" "$AVT_BASE_DIR/done" "$AVT_BASE_DIR/logs"

find_python() {
  if [ -n "${AVT_PYTHON_BIN:-}" ] && [ -x "${AVT_PYTHON_BIN:-}" ]; then
    echo "$AVT_PYTHON_BIN"
    return 0
  fi
  if [ -x "$VENV_PYTHON" ]; then
    echo "$VENV_PYTHON"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  return 1
}

if [ -f "$PID_FILE" ]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Watcher is already running with PID $OLD_PID."
    echo "Inbox:  $AVT_BASE_DIR/inbox"
    echo "Output: $AVT_BASE_DIR/output"
    echo "Done:   $AVT_BASE_DIR/done"
    echo "Logs:   $AVT_BASE_DIR/logs"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

PYTHON_BIN="$(find_python || true)"
if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3 was not found. Please install Python 3 first."
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import watchdog' >/dev/null 2>&1; then
  echo "watchdog is not installed for:"
  echo "  $PYTHON_BIN"
  echo
  echo "Run:"
  echo "  $SCRIPT_DIR/install_whisper.sh"
  echo "or:"
  echo "  $SCRIPT_DIR/install.sh"
  exit 1
fi

nohup "$PYTHON_BIN" "$SCRIPT_DIR/watch_inbox.py" >"$OUT_LOG" 2>"$ERR_LOG" &
WATCHER_PID="$!"
echo "$WATCHER_PID" > "$PID_FILE"

echo "Started watcher with PID $WATCHER_PID."
echo "Inbox:  $AVT_BASE_DIR/inbox"
echo "Output: $AVT_BASE_DIR/output"
echo "Done:   $AVT_BASE_DIR/done"
echo "Logs:   $AVT_BASE_DIR/logs"

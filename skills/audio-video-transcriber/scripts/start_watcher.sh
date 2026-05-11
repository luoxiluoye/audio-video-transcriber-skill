#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
VENV_PYTHON="${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/python"
DEFAULT_VENV_PYTHON="$HOME/.audio-video-transcriber/venv/bin/python"
COMMON_WHISPER_ENV_PYTHON="$HOME/whisper-env/bin/python"
PID_FILE="$AVT_BASE_DIR/logs/watcher.pid"
OUT_LOG="$AVT_BASE_DIR/logs/watcher.out.log"
ERR_LOG="$AVT_BASE_DIR/logs/watcher.err.log"

mkdir -p "$AVT_BASE_DIR/inbox" "$AVT_BASE_DIR/output" "$AVT_BASE_DIR/done" "$AVT_BASE_DIR/logs"

find_python() {
  local candidates=()
  local whisper_path=""
  local python3_path=""
  if [ -n "${AVT_PYTHON_BIN:-}" ]; then
    candidates+=("$AVT_PYTHON_BIN")
  fi
  candidates+=("$VENV_PYTHON" "$DEFAULT_VENV_PYTHON")
  if [ -n "${AVT_WHISPER_BIN:-}" ]; then
    whisper_path="$AVT_WHISPER_BIN"
    candidates+=("$(dirname "$whisper_path")/python")
  elif command -v whisper >/dev/null 2>&1; then
    whisper_path="$(command -v whisper)"
    candidates+=("$(dirname "$whisper_path")/python")
  fi
  candidates+=("$COMMON_WHISPER_ENV_PYTHON")
  if command -v python3 >/dev/null 2>&1; then
    python3_path="$(command -v python3)"
    candidates+=("$python3_path")
  fi

  local candidate
  for candidate in "${candidates[@]}"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ] && "$candidate" -c 'import watchdog' >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  for candidate in "${candidates[@]}"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
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
  if [ -x "${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/whisper" ]; then
    echo "${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}/bin/whisper"
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

export AVT_BASE_DIR
export AVT_PYTHON_BIN="${AVT_PYTHON_BIN:-$PYTHON_BIN}"
WHISPER_BIN="$(find_whisper || true)"
if [ -n "$WHISPER_BIN" ]; then
  export AVT_WHISPER_BIN="${AVT_WHISPER_BIN:-$WHISPER_BIN}"
fi

if ! "$AVT_PYTHON_BIN" -c 'import watchdog' >/dev/null 2>&1; then
  echo "watchdog is not installed for:"
  echo "  $AVT_PYTHON_BIN"
  echo
  echo "Run:"
  echo "  $SCRIPT_DIR/install_whisper.sh"
  echo "or:"
  echo "  $SCRIPT_DIR/install.sh"
  exit 1
fi

nohup "$AVT_PYTHON_BIN" "$SCRIPT_DIR/watch_inbox.py" >"$OUT_LOG" 2>"$ERR_LOG" &
WATCHER_PID="$!"
disown "$WATCHER_PID" 2>/dev/null || true
echo "$WATCHER_PID" > "$PID_FILE"

sleep 1
if ! kill -0 "$WATCHER_PID" 2>/dev/null; then
  rm -f "$PID_FILE"
  echo "Watcher failed to stay running. Recent error log:"
  tail -20 "$ERR_LOG" 2>/dev/null || true
  echo
  echo "Recent output log:"
  tail -20 "$OUT_LOG" 2>/dev/null || true
  exit 1
fi

echo "Started watcher with PID $WATCHER_PID."
echo "Inbox:  $AVT_BASE_DIR/inbox"
echo "Output: $AVT_BASE_DIR/output"
echo "Done:   $AVT_BASE_DIR/done"
echo "Logs:   $AVT_BASE_DIR/logs"

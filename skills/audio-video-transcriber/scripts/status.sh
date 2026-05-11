#!/usr/bin/env bash
set -euo pipefail

AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
AVT_VENV_DIR_VALUE="${AVT_VENV_DIR:-$HOME/.audio-video-transcriber/venv}"
DEFAULT_VENV_DIR="$HOME/.audio-video-transcriber/venv"
COMMON_WHISPER_ENV_DIR="$HOME/whisper-env"
PID_FILE="$AVT_BASE_DIR/logs/watcher.pid"

find_python() {
  if [ -f "$PID_FILE" ]; then
    PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
      WATCHER_PYTHON="$(ps -p "$PID" -o command= 2>/dev/null | awk '{print $1}' || true)"
      if [ -n "$WATCHER_PYTHON" ] && [ -x "$WATCHER_PYTHON" ]; then
        echo "$WATCHER_PYTHON"
        return 0
      fi
    fi
  fi
  if [ -n "${AVT_PYTHON_BIN:-}" ] && [ -x "${AVT_PYTHON_BIN:-}" ]; then
    echo "$AVT_PYTHON_BIN"
    return 0
  fi
  if [ -x "$AVT_VENV_DIR_VALUE/bin/python" ]; then
    echo "$AVT_VENV_DIR_VALUE/bin/python"
    return 0
  fi
  if [ -x "$DEFAULT_VENV_DIR/bin/python" ]; then
    echo "$DEFAULT_VENV_DIR/bin/python"
    return 0
  fi
  if [ -x "$COMMON_WHISPER_ENV_DIR/bin/python" ]; then
    echo "$COMMON_WHISPER_ENV_DIR/bin/python"
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
  if [ -x "$DEFAULT_VENV_DIR/bin/whisper" ]; then
    echo "$DEFAULT_VENV_DIR/bin/whisper"
    return 0
  fi
  if [ -x "$COMMON_WHISPER_ENV_DIR/bin/whisper" ]; then
    echo "$COMMON_WHISPER_ENV_DIR/bin/whisper"
    return 0
  fi
  PYTHON_PATH="$(find_python || true)"
  if [ -n "$PYTHON_PATH" ]; then
    PYTHON_DIR="$(dirname "$PYTHON_PATH")"
    if [ -x "$PYTHON_DIR/whisper" ]; then
      echo "$PYTHON_DIR/whisper"
      return 0
    fi
  fi
  return 1
}

print_log() {
  local path="$1"
  echo
  echo "Last 20 lines: $path"
  if [ -f "$path" ]; then
    tail -n 20 "$path"
  else
    echo "  No log file yet."
  fi
}

mkdir -p "$AVT_BASE_DIR/inbox" "$AVT_BASE_DIR/output" "$AVT_BASE_DIR/done" "$AVT_BASE_DIR/logs"

echo "Audio Video Transcriber status"
echo
echo "Base dir: $AVT_BASE_DIR"
echo "Inbox:    $AVT_BASE_DIR/inbox"
echo "Output:   $AVT_BASE_DIR/output"
echo "Done:     $AVT_BASE_DIR/done"
echo "Logs:     $AVT_BASE_DIR/logs"
echo

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    echo "Watcher:  running (PID $PID)"
  else
    echo "Watcher:  not running (stale PID file)"
  fi
else
  echo "Watcher:  not running"
fi

echo "Whisper:  $(find_whisper || echo "not found")"
echo "Python:   $(find_python || echo "not found")"

print_log "$AVT_BASE_DIR/logs/transcriber.log"
print_log "$AVT_BASE_DIR/logs/watcher.log"
print_log "$AVT_BASE_DIR/logs/watcher.out.log"
print_log "$AVT_BASE_DIR/logs/watcher.err.log"

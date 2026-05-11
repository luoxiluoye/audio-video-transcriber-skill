#!/usr/bin/env bash
set -euo pipefail

AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
PID_FILE="$AVT_BASE_DIR/logs/watcher.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Watcher is not running. No PID file found."
  exit 0
fi

PID="$(cat "$PID_FILE" 2>/dev/null || true)"
if [ -z "$PID" ]; then
  rm -f "$PID_FILE"
  echo "Watcher is not running. Removed empty PID file."
  exit 0
fi

if kill -0 "$PID" 2>/dev/null; then
  echo "Stopping watcher with PID $PID..."
  kill "$PID"
  sleep 1
  if kill -0 "$PID" 2>/dev/null; then
    echo "Watcher is still shutting down. Check status in a moment."
  else
    echo "Watcher stopped."
    rm -f "$PID_FILE"
  fi
else
  echo "Watcher is not running. Removed stale PID file."
  rm -f "$PID_FILE"
fi

#!/usr/bin/env bash
set -euo pipefail

AVT_BASE_DIR="${AVT_BASE_DIR:-$HOME/AudioVideoTranscriber}"
INBOX_DIR="$AVT_BASE_DIR/inbox"
OUTPUT_DIR="$AVT_BASE_DIR/output"
DONE_DIR="$AVT_BASE_DIR/done"
LOG_DIR="$AVT_BASE_DIR/logs"
TIMEOUT_SECONDS="${AVT_TEST_WATCH_TIMEOUT:-900}"

usage() {
  cat <<'EOF'
Usage:
  ./skills/audio-video-transcriber/scripts/test_watcher.sh "/path/to/file.m4a" [timeout_seconds]

Copies a media file into the watcher inbox with a unique name, then waits until
matching output or done files appear.
EOF
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

if [ "$#" -lt 1 ]; then
  echo "Missing input media file."
  echo
  usage
  exit 1
fi

SOURCE_FILE="$1"
if [ "$#" -ge 2 ]; then
  TIMEOUT_SECONDS="$2"
fi

if [ ! -f "$SOURCE_FILE" ]; then
  echo "File not found: $SOURCE_FILE"
  exit 1
fi

mkdir -p "$INBOX_DIR" "$OUTPUT_DIR" "$DONE_DIR" "$LOG_DIR"

PID_FILE="$LOG_DIR/watcher.pid"
WATCHER_PID=""
if [ -f "$PID_FILE" ]; then
  WATCHER_PID="$(cat "$PID_FILE" 2>/dev/null || true)"
fi
if [ -z "$WATCHER_PID" ] || ! kill -0 "$WATCHER_PID" 2>/dev/null; then
  echo "Watcher does not appear to be running."
  echo "Start it first:"
  echo "  ./bin/avt watch"
  exit 1
fi

BASENAME="$(basename "$SOURCE_FILE")"
STEM="${BASENAME%.*}"
EXT="${BASENAME##*.}"
STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET_NAME="${STEM}-watch-test-${STAMP}.${EXT}"
TARGET_FILE="$INBOX_DIR/$TARGET_NAME"
TARGET_STEM="${TARGET_NAME%.*}"

echo "Copying test file into inbox:"
echo "  $TARGET_FILE"
cp "$SOURCE_FILE" "$TARGET_FILE"

echo "Waiting up to $TIMEOUT_SECONDS seconds for watcher output..."
START_TIME="$(date +%s)"
while true; do
  if ls "$OUTPUT_DIR/$TARGET_STEM".* >/dev/null 2>&1; then
    echo "Output detected:"
    ls -la "$OUTPUT_DIR/$TARGET_STEM".*
    exit 0
  fi
  if [ -f "$DONE_DIR/$TARGET_NAME" ]; then
    echo "Done file detected:"
    ls -la "$DONE_DIR/$TARGET_NAME"
    exit 0
  fi

  NOW="$(date +%s)"
  if [ $((NOW - START_TIME)) -ge "$TIMEOUT_SECONDS" ]; then
    echo "Timed out waiting for watcher output."
    echo "Recent watcher logs:"
    tail -40 "$LOG_DIR/watcher.log" 2>/dev/null || true
    tail -40 "$LOG_DIR/watcher.err.log" 2>/dev/null || true
    exit 1
  fi
  sleep 5
done

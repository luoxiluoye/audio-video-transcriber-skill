#!/usr/bin/env python3
"""Watch the local inbox folder and transcribe new media files."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print(
        "watchdog is not installed.\n\n"
        "Try:\n"
        "  ./skills/audio-video-transcriber/scripts/install_whisper.sh\n"
        "or:\n"
        "  ./skills/audio-video-transcriber/scripts/install.sh",
        file=sys.stderr,
    )
    raise


SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".flac",
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
}

DEFAULT_BASE_DIR = Path("~/AudioVideoTranscriber").expanduser()


def expand_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def get_base_dir() -> Path:
    return expand_path(os.environ.get("AVT_BASE_DIR", str(DEFAULT_BASE_DIR)))


def create_work_dirs(base_dir: Path) -> dict[str, Path]:
    dirs = {
        "base": base_dir,
        "inbox": base_dir / "inbox",
        "output": base_dir / "output",
        "done": base_dir / "done",
        "logs": base_dir / "logs",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "watcher.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def python_bin() -> str:
    return os.environ.get("AVT_PYTHON_BIN") or sys.executable


def is_supported(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


class InboxHandler(FileSystemEventHandler):
    def __init__(self, script_dir: Path) -> None:
        self.script_dir = script_dir
        self.seen: set[Path] = set()

    def on_created(self, event) -> None:  # type: ignore[no-untyped-def]
        if not event.is_directory:
            self.handle(Path(event.src_path))

    def on_moved(self, event) -> None:  # type: ignore[no-untyped-def]
        if not event.is_directory:
            self.handle(Path(event.dest_path))

    def handle(self, path: Path) -> None:
        path = path.expanduser().resolve()
        if path in self.seen:
            return
        if not is_supported(path):
            logging.info("Ignoring unsupported file: %s", path)
            return

        self.seen.add(path)
        print(f"New media file detected: {path}")
        logging.info("New media file detected: %s", path)

        command = [
            python_bin(),
            str(self.script_dir / "transcribe.py"),
            str(path),
            "--move-done",
        ]
        try:
            subprocess.run(command, check=True)
            logging.info("Finished transcribing: %s", path)
        except subprocess.CalledProcessError:
            logging.exception("Transcription failed for: %s", path)
            print(f"Transcription failed. Check logs for details: {path}", file=sys.stderr)


def main() -> int:
    base_dir = get_base_dir()
    dirs = create_work_dirs(base_dir)
    setup_logging(dirs["logs"])
    script_dir = Path(__file__).resolve().parent

    print("Audio Video Transcriber watcher is running.")
    print(f"Inbox:  {dirs['inbox']}")
    print(f"Output: {dirs['output']}")
    print(f"Done:   {dirs['done']}")
    print(f"Logs:   {dirs['logs']}")
    logging.info("Watching inbox: %s", dirs["inbox"])

    observer = Observer()
    observer.schedule(InboxHandler(script_dir), str(dirs["inbox"]), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping watcher...")
        logging.info("Stopping watcher after keyboard interrupt.")
    finally:
        observer.stop()
        observer.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

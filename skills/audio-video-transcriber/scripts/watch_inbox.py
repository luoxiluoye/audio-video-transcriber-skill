#!/usr/bin/env python3
"""Watch the local inbox folder and transcribe new media files."""

from __future__ import annotations

import logging
import os
import queue
import subprocess
import sys
import threading
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


def wait_for_complete_copy(path: Path, stable_checks: int = 3, delay: float = 2.0) -> None:
    previous_size = -1
    stable_count = 0
    logging.info("Waiting for file to finish copying: %s", path)
    while stable_count < stable_checks:
        if not path.exists():
            raise FileNotFoundError(f"File disappeared before processing: {path}")
        current_size = path.stat().st_size
        if current_size == previous_size and current_size > 0:
            stable_count += 1
            logging.info(
                "File size stable check %s/%s for %s (%s bytes)",
                stable_count,
                stable_checks,
                path,
                current_size,
            )
        else:
            if previous_size != -1:
                logging.info("File size changed for %s: %s -> %s bytes", path, previous_size, current_size)
            previous_size = current_size
            stable_count = 0
        time.sleep(delay)


class InboxHandler(FileSystemEventHandler):
    def __init__(self, script_dir: Path) -> None:
        self.script_dir = script_dir
        self.queue: queue.Queue[Path] = queue.Queue()
        self.queued: set[Path] = set()
        self.processing: set[Path] = set()
        self.completed: set[Path] = set()
        self.lock = threading.Lock()

    def on_created(self, event) -> None:  # type: ignore[no-untyped-def]
        if not event.is_directory:
            self.enqueue(Path(event.src_path), "created")

    def on_moved(self, event) -> None:  # type: ignore[no-untyped-def]
        if not event.is_directory:
            self.enqueue(Path(event.dest_path), "moved")

    def on_modified(self, event) -> None:  # type: ignore[no-untyped-def]
        if not event.is_directory:
            self.enqueue(Path(event.src_path), "modified")

    def enqueue(self, path: Path, reason: str) -> None:
        path = path.expanduser().resolve()
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logging.info("Skipping unsupported file event (%s): %s", reason, path)
            return

        with self.lock:
            if path in self.completed:
                logging.info("Skipping already completed file event (%s): %s", reason, path)
                return
            if path in self.queued or path in self.processing:
                logging.info("Skipping duplicate file event (%s): %s", reason, path)
                return
            self.queued.add(path)

        logging.info("Queued media file from %s event: %s", reason, path)
        print(f"Queued media file: {path}", flush=True)
        self.queue.put(path)

    def scan_existing(self, inbox_dir: Path) -> None:
        logging.info("Scanning existing inbox files: %s", inbox_dir)
        for path in sorted(inbox_dir.iterdir()):
            if path.is_file():
                self.enqueue(path, "startup-scan")

    def start_worker(self) -> threading.Thread:
        worker = threading.Thread(target=self.worker_loop, name="avt-worker", daemon=True)
        worker.start()
        return worker

    def worker_loop(self) -> None:
        while True:
            path = self.queue.get()
            try:
                self.process(path)
            finally:
                self.queue.task_done()

    def process(self, path: Path) -> None:
        with self.lock:
            self.queued.discard(path)
            self.processing.add(path)

        try:
            if not is_supported(path):
                logging.info("Skipping missing or unsupported file before processing: %s", path)
                return

            logging.info("Starting transcription job: %s", path)
            print(f"Starting transcription: {path}", flush=True)
            wait_for_complete_copy(path)

            command = [
                python_bin(),
                str(self.script_dir / "transcribe.py"),
                str(path),
                "--move-done",
                "--no-wait",
            ]
            logging.info("Running command: %s", " ".join(command))
            subprocess.run(command, check=True)
            logging.info("Completed transcription job: %s", path)
            print(f"Completed transcription: {path}", flush=True)
            with self.lock:
                self.completed.add(path)
        except subprocess.CalledProcessError as exc:
            logging.exception("Transcription command failed for %s with exit code %s", path, exc.returncode)
            print(f"Transcription failed. Check logs for details: {path}", file=sys.stderr, flush=True)
        except Exception:
            logging.exception("Transcription failed for: %s", path)
            print(f"Transcription failed. Check logs for details: {path}", file=sys.stderr, flush=True)
        finally:
            with self.lock:
                self.processing.discard(path)

    def handle(self, path: Path) -> None:
        # Backward-compatible helper for tests and older callers.
        self.enqueue(path, "manual")


def log_environment(dirs: dict[str, Path]) -> None:
    logging.info("Inbox: %s", dirs["inbox"])
    logging.info("Output: %s", dirs["output"])
    logging.info("Done: %s", dirs["done"])
    logging.info("Logs: %s", dirs["logs"])
    logging.info("AVT_BASE_DIR=%s", os.environ.get("AVT_BASE_DIR", "not set"))
    logging.info("AVT_PYTHON_BIN=%s", os.environ.get("AVT_PYTHON_BIN", "not set"))
    logging.info("AVT_WHISPER_BIN=%s", os.environ.get("AVT_WHISPER_BIN", "not set"))
    logging.info("Python executable=%s", python_bin())


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
    log_environment(dirs)

    observer = Observer()
    handler = InboxHandler(script_dir)
    handler.start_worker()
    handler.scan_existing(dirs["inbox"])
    observer.schedule(handler, str(dirs["inbox"]), recursive=False)
    observer.start()
    logging.info("Watching inbox for created, moved, and modified events: %s", dirs["inbox"])

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

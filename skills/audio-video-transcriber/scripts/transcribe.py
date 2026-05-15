#!/usr/bin/env python3
"""Transcribe one local audio/video file with a local Whisper CLI."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


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
DEFAULT_VENV_DIR = Path("~/.audio-video-transcriber/venv").expanduser()
DEFAULT_VENV_WHISPER_CANDIDATES = (
    DEFAULT_VENV_DIR / "bin" / "whisper",
    DEFAULT_VENV_DIR / "bin" / "whisper.exe",
    DEFAULT_VENV_DIR / "Scripts" / "whisper.exe",
    DEFAULT_VENV_DIR / "Scripts" / "whisper",
    Path("~/whisper-env/bin/whisper").expanduser(),
    Path("~/whisper-env/bin/whisper.exe").expanduser(),
)


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected true or false, got {value!r}.")


def expand_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def base_dir_from_env_or_arg(value: str | None) -> Path:
    if value:
        return expand_path(value)
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
            logging.FileHandler(log_dir / "transcriber.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def resolve_executable(candidate: str | None) -> str | None:
    if not candidate:
        return None
    expanded = os.path.expanduser(candidate)
    if os.sep in expanded or (os.altsep and os.altsep in expanded):
        path = Path(expanded)
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
        return None
    return shutil.which(expanded)


def find_whisper(cli_value: str | None) -> str | None:
    configured = resolve_executable(cli_value) or resolve_executable(os.environ.get("AVT_WHISPER_BIN"))
    if configured:
        return configured

    path_whisper = shutil.which("whisper")
    if path_whisper:
        return path_whisper

    env_venv = os.environ.get("AVT_VENV_DIR")
    candidates = []
    if env_venv:
        venv_dir = expand_path(env_venv)
        candidates.extend(
            [
                venv_dir / "bin" / "whisper",
                venv_dir / "bin" / "whisper.exe",
                venv_dir / "Scripts" / "whisper.exe",
                venv_dir / "Scripts" / "whisper",
            ]
        )
    python_bin = os.environ.get("AVT_PYTHON_BIN") or sys.executable
    if python_bin:
        python_dir = expand_path(python_bin).parent
        candidates.extend(
            [
                python_dir / "whisper",
                python_dir / "whisper.exe",
            ]
        )
    candidates.extend(DEFAULT_VENV_WHISPER_CANDIDATES)

    for candidate in candidates:
        resolved = resolve_executable(str(candidate))
        if resolved:
            return resolved
    return None


def wait_for_complete_copy(path: Path, stable_checks: int = 3, delay: float = 2.0) -> None:
    logging.info("Waiting for file copy to finish: %s", path)
    previous_size = -1
    stable_count = 0
    while stable_count < stable_checks:
        if not path.exists():
            raise FileNotFoundError(f"The file disappeared before transcription: {path}")
        current_size = path.stat().st_size
        if current_size == previous_size and current_size > 0:
            stable_count += 1
        else:
            stable_count = 0
            previous_size = current_size
        time.sleep(delay)


def unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a safe destination name for {path}.")


def expected_outputs(input_path: Path, output_dir: Path) -> list[Path]:
    return sorted(output_dir.glob(f"{input_path.stem}.*"))


def find_transcript_output(input_path: Path, output_dir: Path) -> Path | None:
    for suffix in (".txt", ".vtt", ".srt", ".tsv", ".json"):
        candidate = output_dir / f"{input_path.stem}{suffix}"
        if candidate.exists():
            return candidate
    return None


def create_review_files(input_path: Path, output_dir: Path, overwrite: bool = False) -> None:
    transcript_path = find_transcript_output(input_path, output_dir)
    if not transcript_path:
        logging.info("Skipping review files because no transcript output was found for: %s", input_path)
        return

    command = [
        sys.executable,
        str(Path(__file__).resolve().parent / "postprocess.py"),
        str(transcript_path),
        "--source-file",
        str(input_path),
        "--output-dir",
        str(output_dir),
    ]
    if overwrite:
        command.append("--overwrite")
    logging.info("Creating review files for %s", transcript_path)
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        logging.warning("Could not create review files for %s: %s", transcript_path, exc)


def run_whisper(
    whisper_bin: str,
    input_path: Path,
    output_dir: Path,
    model: str,
    language: str,
    output_format: str,
) -> None:
    command = [
        whisper_bin,
        str(input_path),
        "--model",
        model,
        "--output_dir",
        str(output_dir),
        "--output_format",
        output_format,
    ]
    if language.strip().lower() != "auto":
        command.extend(["--language", language])

    logging.info("Running Whisper on %s", input_path)
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Whisper could not finish this transcription. "
            "Please check that ffmpeg is installed and the media file is readable."
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe one local audio/video file with Whisper."
    )
    parser.add_argument("input", help="Path to an audio or video file.")
    parser.add_argument("--model", default=os.environ.get("AVT_MODEL", "small"))
    parser.add_argument("--language", default=os.environ.get("AVT_LANGUAGE", "Chinese"))
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--base-dir", default=None)
    parser.add_argument(
        "--move-done",
        nargs="?",
        const=True,
        default=False,
        type=parse_bool,
        help="Move the source file to the done directory after successful transcription.",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not wait for the file size to stabilize before transcribing.",
    )
    parser.add_argument("--format", default="all", help="Whisper output format.")
    parser.add_argument("--whisper-bin", default=None, help="Path to the Whisper CLI.")
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Do not create transcript Word, summary, or correction review deliverables after transcription.",
    )
    parser.add_argument(
        "--overwrite-review",
        action="store_true",
        help="Overwrite existing review deliverables.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_dir = base_dir_from_env_or_arg(args.base_dir)
    dirs = create_work_dirs(base_dir)
    setup_logging(dirs["logs"])

    input_path = expand_path(args.input)
    output_dir = expand_path(args.output_dir) if args.output_dir else dirs["output"]
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        if not input_path.is_file():
            raise ValueError(f"This path is not a file: {input_path}")
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            supported = ", ".join(sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS))
            raise ValueError(f"Unsupported file type: {input_path.suffix}. Supported: {supported}")

        whisper_bin = find_whisper(args.whisper_bin)
        if not whisper_bin:
            raise RuntimeError(
                "Whisper CLI not found.\n\n"
                "Try:\n"
                "  ./skills/audio-video-transcriber/scripts/install_whisper.sh\n\n"
                "Or set:\n"
                '  export AVT_WHISPER_BIN="/path/to/whisper"'
            )

        existing_txt = output_dir / f"{input_path.stem}.txt"
        if existing_txt.exists():
            logging.info("Skipping because output already exists: %s", existing_txt)
            print(f"Already transcribed, skipping: {existing_txt}")
            if not args.no_review:
                create_review_files(input_path, output_dir, overwrite=args.overwrite_review)
            return 0

        if not args.no_wait:
            wait_for_complete_copy(input_path)

        run_whisper(
            whisper_bin=whisper_bin,
            input_path=input_path,
            output_dir=output_dir,
            model=args.model,
            language=args.language,
            output_format=args.format,
        )

        outputs = expected_outputs(input_path, output_dir)
        if outputs:
            print("Transcription complete. Output files:")
            for path in outputs:
                print(f"  {path}")
                logging.info("Output file: %s", path)
        else:
            print(f"Transcription finished, but no output files were found in {output_dir}.")
            logging.warning("No output files found for %s in %s", input_path, output_dir)

        if not args.no_review:
            create_review_files(input_path, output_dir, overwrite=args.overwrite_review)

        if args.move_done:
            destination = unique_destination(dirs["done"] / input_path.name)
            shutil.move(str(input_path), str(destination))
            print(f"Moved source file to: {destination}")
            logging.info("Moved source file to %s", destination)

        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should print friendly errors.
        logging.error("%s", exc)
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

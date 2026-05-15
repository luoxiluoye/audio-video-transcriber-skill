#!/usr/bin/env python3
"""MCP server exposing the local Audio Video Transcriber scripts."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parents[1]

# The repository intentionally has a top-level mcp/ directory. Remove the
# repository root from import lookup before importing the official SDK package
# so local files do not shadow `mcp.server.fastmcp`.
for entry in ("", str(ROOT_DIR)):
    if entry in sys.path:
        sys.path.remove(entry)

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError as exc:
    print(
        "MCP Python SDK is not installed.\n\n"
        "Install it from the repository root with:\n"
        "  python3 -m venv .venv\n"
        "  . .venv/bin/activate\n"
        "  python -m pip install -r mcp/requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

mcp = FastMCP("audio-video-transcriber")

SCRIPTS_DIR = ROOT_DIR / "skills" / "audio-video-transcriber" / "scripts"


def script_path(name: str) -> Path:
    path = SCRIPTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Required project script was not found: {path}")
    return path


def run_command(command: list[str], env_overrides: dict[str, str] | None = None) -> dict[str, Any]:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    result = subprocess.run(
        command,
        cwd=ROOT_DIR,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    output = result.stdout
    if result.stderr:
        output = f"{output}\n{result.stderr}".strip()

    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "output": output.strip(),
        "command": command,
    }


def configured_python() -> str:
    return os.environ.get("AVT_PYTHON_BIN") or "python3"


@mcp.tool()
def transcribe_file(
    input_path: str,
    model: str = "small",
    language: str = "Chinese",
    output_format: str = "all",
    move_done: bool = False,
) -> dict[str, Any]:
    """Transcribe a local audio/video file with the project transcribe.py script."""
    media_path = Path(input_path).expanduser()
    command = [
        configured_python(),
        str(script_path("transcribe.py")),
        str(media_path),
        "--model",
        model,
        "--language",
        language,
        "--format",
        output_format,
    ]
    if move_done:
        command.append("--move-done")
    return run_command(command)


@mcp.tool()
def postprocess_transcript(
    transcript_path: str,
    source_file: str = "",
    output_dir: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create agent-ready summary and correction Markdown files for a transcript."""
    command = [
        configured_python(),
        str(script_path("postprocess.py")),
        str(Path(transcript_path).expanduser()),
    ]
    if source_file:
        command.extend(["--source-file", str(Path(source_file).expanduser())])
    if output_dir:
        command.extend(["--output-dir", str(Path(output_dir).expanduser())])
    if overwrite:
        command.append("--overwrite")
    return run_command(command)


@mcp.tool()
def start_watcher(base_dir: str | None = None) -> dict[str, Any]:
    """Start the local inbox watcher."""
    env_overrides = {}
    if base_dir:
        env_overrides["AVT_BASE_DIR"] = str(Path(base_dir).expanduser())
    return run_command([str(script_path("start_watcher.sh"))], env_overrides)


@mcp.tool()
def stop_watcher() -> dict[str, Any]:
    """Stop the local inbox watcher."""
    return run_command([str(script_path("stop_watcher.sh"))])


@mcp.tool()
def status() -> dict[str, Any]:
    """Return current local transcriber status and recent logs."""
    return run_command([str(script_path("status.sh"))])


@mcp.tool()
def doctor() -> dict[str, Any]:
    """Run the local environment doctor."""
    return run_command([str(script_path("doctor.sh"))])


@mcp.tool()
def bootstrap(yes: bool = False) -> dict[str, Any]:
    """Initialize local folders and optionally install the Python Whisper environment."""
    command = [str(script_path("bootstrap.sh"))]
    if yes:
        command.append("--yes")
    return run_command(command)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

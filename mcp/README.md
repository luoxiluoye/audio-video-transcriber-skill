# Audio Video Transcriber MCP Server

This optional MCP server exposes the local Audio Video Transcriber Toolkit to MCP-compatible agents.

It is a thin wrapper over the project scripts. It does not upload files, call cloud APIs, run `sudo`, or reimplement transcription logic.

## Install

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -r mcp/requirements.txt
```

## Run

```bash
python3 mcp/server.py
```

Most MCP clients start the server for you using `.mcp.json`.

## Tools

- `transcribe_file`: transcribe a local audio/video file.
- `start_watcher`: start the local inbox watcher.
- `stop_watcher`: stop the watcher.
- `status`: show watcher status, paths, and recent logs.
- `doctor`: check Python, Whisper, ffmpeg, watchdog, and environment variables.
- `bootstrap`: initialize local folders and optionally install the Python Whisper environment.

## Configuration

The server reads the same environment variables as the CLI:

```bash
export AVT_BASE_DIR="$HOME/AudioVideoTranscriber"
export AVT_MODEL="small"
export AVT_LANGUAGE="Chinese"
export AVT_WHISPER_BIN="/path/to/whisper"
export AVT_PYTHON_BIN="/path/to/python"
export AVT_VENV_DIR="$HOME/.audio-video-transcriber/venv"
```

## Client Notes

`.mcp.json` is a reference configuration. Different agents and editors may use different MCP configuration file names or schemas, so adjust paths and environment values for your client.

# Repository Maintenance Notes

This repository provides a local audio/video transcription toolkit with a Codex Plugin, Codex Skill, standalone CLI, and optional MCP server.

## Principles

- Keep the project simple, stable, and locally runnable.
- This project must remain usable without Codex.
- Do not introduce cloud APIs.
- Do not introduce paid services.
- Do not hard-code user paths.
- Do not commit Whisper model weights.
- Do not commit audio or video sample files.
- Do not commit generated transcription outputs.
- Do not run `sudo` from scripts.
- Do not modify user shell configuration files unless explicitly requested.
- Prefer macOS compatibility first, then Linux.
- Recommend WSL for Windows users.
- Windows native must remain supported through PowerShell scripts.
- Do not assume the agent natively supports Codex Skill.
- Do not assume the agent natively supports MCP.
- Always keep CLI fallback available.

## Cross-Agent Compatibility

- Core transcription logic must remain cross-platform Python.
- Bash is only the macOS/Linux/WSL entry layer.
- PowerShell is the Windows native entry layer.
- Keep `./bin/avt` as the stable universal CLI entrypoint.
- Keep `./bin/avt.ps1` as the stable Windows PowerShell CLI entrypoint.
- Keep Codex Skill instructions, CLI commands, and MCP tools consistent.
- Do not duplicate transcription logic in multiple places. Prefer calling `transcribe.py`.
- MCP server should be a thin wrapper over existing scripts.
- Any agent should be able to inspect `README.md` and run the workflow from terminal.
- Agents that do not support Codex Skills should still be able to use `./bin/avt`.
- Agents that do not support MCP should still be able to use `./bin/avt`.

## Code Rules

- Python scripts must have a `main` function.
- Python path handling should use `pathlib`.
- Do not hard-code `/Users/xxx`.
- Do not hard-code `C:\Users\xxx`.
- All paths must come from environment variables, user-provided arguments, or the user's home directory.
- All subprocess calls must avoid `shell=True` unless there is a clear documented reason.
- Shell scripts must use `#!/usr/bin/env bash` and `set -euo pipefail`.
- Shell scripts should stay portable across bash/zsh launch environments.
- Shell scripts must remain executable.
- README commands must match the real scripts.
- `.mcp.json` is a reference config; keep it aligned with `mcp/server.py`.

## Required Checks

After modifying Python scripts, run:

```bash
python3 -m py_compile skills/audio-video-transcriber/scripts/transcribe.py
python3 -m py_compile skills/audio-video-transcriber/scripts/watch_inbox.py
```

After modifying shell scripts, run:

```bash
bash -n skills/audio-video-transcriber/scripts/doctor.sh
bash -n skills/audio-video-transcriber/scripts/install_whisper.sh
bash -n skills/audio-video-transcriber/scripts/bootstrap.sh
bash -n skills/audio-video-transcriber/scripts/install.sh
bash -n skills/audio-video-transcriber/scripts/start_watcher.sh
bash -n skills/audio-video-transcriber/scripts/stop_watcher.sh
bash -n skills/audio-video-transcriber/scripts/status.sh
```

Also run:

```bash
chmod +x skills/audio-video-transcriber/scripts/*.sh
chmod +x skills/audio-video-transcriber/scripts/*.py
./skills/audio-video-transcriber/scripts/doctor.sh
```

After modifying PowerShell scripts, validate them on Windows PowerShell or PowerShell 7 when available:

```powershell
.\bin\avt.ps1 doctor
.\skills\audio-video-transcriber\scripts\doctor.ps1
```

If PowerShell is not available in the current environment, say that clearly in the final notes and still run the Python and Bash checks.

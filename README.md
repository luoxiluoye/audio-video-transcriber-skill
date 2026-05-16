# Audio Video Transcriber Toolkit

A local audio/video transcription toolkit using Whisper.

It includes:

- Codex Plugin
- Codex Skill
- Standalone CLI scripts
- Optional MCP Server

This project works even without Codex. Codex Plugin / Skill is one integration layer, but the core transcription workflow is exposed through normal CLI scripts and an optional MCP server.

一个基于本地 Whisper 的音频/视频转写工具包，用于把音频和视频自动转写为文字与字幕文件。即使不使用 Codex，本项目也可以直接通过终端脚本运行。Codex Plugin / Skill 只是其中一种集成方式；核心转写能力通过普通 CLI 和可选 MCP Server 暴露。

## Features

- Local processing: audio and video files are not uploaded.
- Supports audio and video: `mp3`, `wav`, `m4a`, `aac`, `flac`, `mp4`, `mov`, `mkv`, `avi`, `webm`.
- Outputs Whisper formats such as `txt`, `srt`, `vtt`, `json`, and `tsv`.
- Creates a post-transcription review pack: `*.transcript.docx`, `*.summary.md`, `*.summary.docx`, `*.corrections.md`, and `*.corrections.docx`.
- Optionally creates handoff-friendly HTML: `*.summary.html` and `*.corrections.html`.
- Single-file transcription.
- Inbox watcher workflow for automatic local transcription.
- Auto-detects an existing local Whisper CLI.
- Can initialize an isolated local Python virtual environment for users without Whisper.
- Works as a normal command-line tool without Codex.
- Optional MCP server for MCP-compatible agents.
- Works well in Codex and other agent automation workflows.

## Platform Support

| Platform | Support |
| --- | --- |
| macOS | fully supported |
| Linux | supported |
| Windows WSL | recommended for Windows users |
| Windows native | supported via PowerShell scripts |

## Good For

- Meeting recordings to text
- Interview recordings to text
- Video subtitles
- Course and lecture transcription
- Podcast transcription
- Local batch transcription workflows
- Codex and cross-agent automation workflows

## Use without Codex

Use the universal CLI entrypoint from the repository root:

```bash
./bin/avt doctor
./bin/avt bootstrap
./bin/avt transcribe ~/Desktop/test.mp4
./bin/avt review ~/AudioVideoTranscriber/output/test.txt
./bin/avt watch
./bin/avt stop
./bin/avt status
```

The CLI does not depend on Codex. It is a thin wrapper over the same local scripts used by the Codex Skill and MCP server.

On Windows PowerShell, use:

```powershell
.\bin\avt.ps1 doctor
.\bin\avt.ps1 bootstrap
.\bin\avt.ps1 transcribe "$env:USERPROFILE\Desktop\test.mp4"
.\bin\avt.ps1 review "$env:USERPROFILE\AudioVideoTranscriber\output\test.txt"
.\bin\avt.ps1 watch
.\bin\avt.ps1 stop
.\bin\avt.ps1 status
```

All platforms can also call the Python core directly:

```bash
python skills/audio-video-transcriber/scripts/transcribe.py "path/to/file.mp4"
```

## Install

Clone this repository:

```bash
git clone https://github.com/YOUR-USER/audio-video-transcriber-skill.git
cd audio-video-transcriber-skill
```

Check your local environment:

```bash
./bin/avt doctor
```

If you already have Whisper, run:

```bash
./skills/audio-video-transcriber/scripts/install.sh
```

If you do not have Whisper, run either:

```bash
./bin/avt bootstrap
```

or:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

Optional environment variables:

```bash
export AVT_WHISPER_BIN="/path/to/whisper"
export AVT_PYTHON_BIN="/path/to/python"
export AVT_BASE_DIR="$HOME/AudioVideoTranscriber"
export AVT_MODEL="small"
export AVT_LANGUAGE="Chinese"
```

## If You Already Installed Whisper

Check:

```bash
whisper --help
```

If that works, run:

```bash
./skills/audio-video-transcriber/scripts/install.sh
```

## If You Do Not Have Whisper

Create a local virtual environment and install `openai-whisper`, `watchdog`, and `python-docx`:

```bash
./skills/audio-video-transcriber/scripts/bootstrap.sh --yes
```

or:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

The scripts do not run `sudo` and do not modify your shell startup files.

## Install ffmpeg

Whisper needs `ffmpeg` for most audio and video files.

macOS:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y ffmpeg
```

Windows:

Install ffmpeg and add it to `PATH`. For the smoothest Codex workflow on Windows, use WSL.

## Windows Native PowerShell

Windows native usage is supported through PowerShell scripts. The default working directory is:

```powershell
$env:USERPROFILE\AudioVideoTranscriber
```

Check your environment:

```powershell
.\bin\avt.ps1 doctor
```

Install a local Whisper environment:

```powershell
.\bin\avt.ps1 install
```

or run one-step bootstrap:

```powershell
.\bin\avt.ps1 bootstrap
```

Transcribe a file:

```powershell
.\bin\avt.ps1 transcribe "C:\Users\Name\Desktop\test.mp4"
```

Start and stop the watcher:

```powershell
.\bin\avt.ps1 watch
.\bin\avt.ps1 stop
.\bin\avt.ps1 status
```

You can also run the PowerShell scripts directly:

```powershell
.\skills\audio-video-transcriber\scripts\doctor.ps1
.\skills\audio-video-transcriber\scripts\install_whisper.ps1
.\skills\audio-video-transcriber\scripts\bootstrap.ps1 -Yes
.\skills\audio-video-transcriber\scripts\start_watcher.ps1
.\skills\audio-video-transcriber\scripts\stop_watcher.ps1
.\skills\audio-video-transcriber\scripts\status.ps1
```

The Windows installer checks for `python`, `whisper`, and `ffmpeg`. If Whisper is missing, it creates:

```powershell
$env:USERPROFILE\.audio-video-transcriber\venv
```

and installs:

```powershell
python -m pip install -U pip setuptools wheel
python -m pip install -U openai-whisper watchdog python-docx
```

The scripts do not modify system environment variables automatically. To configure a PowerShell session manually:

```powershell
$env:AVT_BASE_DIR = "$env:USERPROFILE\AudioVideoTranscriber"
$env:AVT_MODEL = "small"
$env:AVT_LANGUAGE = "Chinese"
$env:AVT_VENV_DIR = "$env:USERPROFILE\.audio-video-transcriber\venv"
$env:AVT_PYTHON_BIN = "$env:USERPROFILE\.audio-video-transcriber\venv\Scripts\python.exe"
$env:AVT_WHISPER_BIN = "$env:USERPROFILE\.audio-video-transcriber\venv\Scripts\whisper.exe"
```

If `ffmpeg` is missing, install it and add it to `PATH`. The scripts only print guidance; they do not change system settings.

## Use with Codex

This repository keeps the Codex Plugin and Skill integration in place.

The plugin manifest is:

```text
.codex-plugin/plugin.json
```

The Codex Skill is:

```text
skills/audio-video-transcriber/SKILL.md
```

### Use As A Personal Codex Skill

Copy the skill into your personal Codex skills directory:

```bash
mkdir -p ~/.agents/skills
cp -R skills/audio-video-transcriber ~/.agents/skills/
```

Then in Codex:

```text
Use $audio-video-transcriber to transcribe ~/Desktop/test.mp4
```

You can also install or reference this repository as a Codex Plugin. The plugin manifest references both the skill directory and the optional MCP configuration.

## Use with other coding agents

This repository is agent-readable.

Agents such as Claude Code, Cursor, Windsurf, Gemini CLI, or other coding agents do not need native Codex Skill support to use this project. They can read `README.md` and `AGENTS.md`, then call the stable CLI entrypoint:

```bash
./bin/avt doctor
./bin/avt transcribe ~/Desktop/test.mp4
./bin/avt status
```

The core commands are exposed through `./bin/avt`. Agents that do not support Codex Skills can still use the CLI interface. Agents that support MCP can use the optional MCP server.

## Use with MCP

Install MCP dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -r mcp/requirements.txt
```

Reference MCP config:

```text
.mcp.json
```

Available MCP tools:

- `transcribe_file`
- `postprocess_transcript`
- `start_watcher`
- `stop_watcher`
- `status`
- `doctor`
- `bootstrap`

Different agents and editors can use different MCP configuration formats. Treat `.mcp.json` as a reference and adjust paths, command names, and environment values for your client.

## Single File Transcription

```bash
./bin/avt transcribe ~/Desktop/test.mp4
```

Useful options:

```bash
./bin/avt transcribe ~/Desktop/test.mp4 \
  --model small \
  --language Chinese \
  --format all
```

Use automatic language detection:

```bash
./bin/avt transcribe ~/Desktop/test.mp4 --language auto
```

## Post-Transcription Review Pack

Every successful transcription creates a review pack next to the Whisper outputs:

```text
<name>.transcript.docx
<name>.summary.md
<name>.summary.docx
<name>.corrections.md
<name>.corrections.docx
```

`*.transcript.docx` is the complete transcript in a Word-friendly layout. It includes the source file name, generation time, transcript path, output formats, and paragraphs. When the input transcript has SRT/VTT/Whisper timestamps, the Word transcript preserves those time ranges.

`*.summary.md` and `*.summary.docx` are content-summary workspaces with sections for core summary, key content, key viewpoints, action items, timeline, data and information analysis, and highlight summary.

`*.corrections.md` and `*.corrections.docx` are correction workspaces with tables for likely recognition errors, proper noun normalization, sentence polishing notes, and a corrected-text section.

The review pack is local and deterministic. It does not call an LLM API or upload media/transcripts. Without Codex or another capable agent, the summary and corrections files are structured templates, not finished editorial analysis. In an agent workflow, ask the agent to read the transcript and complete the Markdown, Word, and optional HTML deliverables.

There are two review commands:

- `review` creates the initial review pack from a transcript.
- `review-sync` reads the current `*.summary.md` and `*.corrections.md` content after a user or agent has edited them, then regenerates the matching DOCX/HTML deliverables from that finished Markdown.

Create the review pack for an existing transcript:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt
```

Generate HTML versions too:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --html
```

Generate every supported review format:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --all
```

Keep the old Markdown-only behavior:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --markdown-only
```

After Codex or another agent fills the Markdown files, sync the final content to Word and HTML:

```bash
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.summary.md
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.corrections.md
```

Or sync both sibling Markdown files from the transcript path:

```bash
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.txt --all
```

`review-sync` overwrites the matching `*.summary.docx`, `*.corrections.docx`, `*.summary.html`, and `*.corrections.html` so they reflect the latest Markdown content.

Skip review-pack generation for one transcription:

```bash
./bin/avt transcribe ~/Desktop/test.mp4 --no-review
```

Overwrite existing review files:

```bash
./bin/avt transcribe ~/Desktop/test.mp4 --overwrite-review
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --overwrite
```

Word output uses the Python package `python-docx`. If it is missing, transcription still succeeds and the review step prints a warning. Install it with:

```bash
python -m pip install -U python-docx
```

`./bin/avt doctor` prints the exact Python path it is checking and, when `python-docx` is missing, prints a copyable install command for that Python.

HTML output is standalone: CSS is embedded in each file, so it can be opened directly or copied into web pages, Feishu Docs, Notion, or public-account drafts.

### Typical Agent Workflow

1. Run `./bin/avt transcribe ~/Desktop/test.mp4`.
2. Let the agent read `~/AudioVideoTranscriber/output/test.txt`.
3. Let the agent fill `test.summary.md` and `test.corrections.md`.
4. Run `./bin/avt review-sync ~/AudioVideoTranscriber/output/test.txt --all`.
5. Deliver `test.transcript.docx`, `test.summary.docx`, `test.corrections.docx`, or the HTML versions depending on where the user needs to paste/share the result.

## Automatic Inbox Watcher

Start the watcher:

```bash
./bin/avt watch
open ~/AudioVideoTranscriber/inbox
```

Drop audio or video files into the inbox. The watcher writes outputs and moves completed source files to `done`.

Stop the watcher:

```bash
./bin/avt stop
```

Check status:

```bash
./bin/avt status
```

## Output Directories

Default directories:

```text
~/AudioVideoTranscriber/inbox
~/AudioVideoTranscriber/output
~/AudioVideoTranscriber/done
~/AudioVideoTranscriber/logs
```

The default output folder contains Whisper outputs such as `json`, `srt`, `tsv`, `txt`, and `vtt`, plus review-pack files such as `*.transcript.docx`, `*.summary.md`, `*.summary.docx`, `*.corrections.md`, and `*.corrections.docx`.

Change them with:

```bash
export AVT_BASE_DIR="$HOME/AudioVideoTranscriber"
```

## Environment Variables

```bash
export AVT_WHISPER_BIN="/path/to/whisper"
export AVT_PYTHON_BIN="/path/to/python"
export AVT_BASE_DIR="$HOME/AudioVideoTranscriber"
export AVT_MODEL="small"
export AVT_LANGUAGE="Chinese"
export AVT_VENV_DIR="$HOME/.audio-video-transcriber/venv"
```

`AVT_LANGUAGE` can be `Chinese`, `English`, or `auto`. When set to `auto`, the script omits Whisper's `--language` argument.

Windows PowerShell example:

```powershell
$env:AVT_WHISPER_BIN = "C:\path\to\whisper.exe"
$env:AVT_PYTHON_BIN = "C:\path\to\python.exe"
$env:AVT_BASE_DIR = "$env:USERPROFILE\AudioVideoTranscriber"
$env:AVT_MODEL = "small"
$env:AVT_LANGUAGE = "Chinese"
$env:AVT_VENV_DIR = "$env:USERPROFILE\.audio-video-transcriber\venv"
```

## Cross-Platform Testing

macOS, Linux, and Windows WSL:

```bash
./bin/avt doctor
./bin/avt transcribe ~/Desktop/test.mp4
./bin/avt status
```

Windows PowerShell:

```powershell
.\bin\avt.ps1 doctor
.\bin\avt.ps1 transcribe "$env:USERPROFILE\Desktop\test.mp4"
.\bin\avt.ps1 status
```

All platforms:

```bash
python skills/audio-video-transcriber/scripts/transcribe.py "path/to/file.mp4"
```

## Why Whisper Is Not Included

- This repository stays lightweight.
- Model weights and large files should not be committed.
- Installation details differ across operating systems.
- Whisper models are downloaded and cached by the user's local environment as needed.
- `ffmpeg` is a system dependency and should be installed by the user.

## First Run Model Download

The first time you run a Whisper model, Whisper may download the model into its local cache. The first transcription can be slower than later runs.

## FAQ

### `whisper not found`

Run:

```bash
./skills/audio-video-transcriber/scripts/doctor.sh
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

Or set:

```bash
export AVT_WHISPER_BIN="/path/to/whisper"
```

### `ffmpeg not found`

Install `ffmpeg` for your system. See the ffmpeg section above.

### `watchdog not found`

Run:

```bash
./skills/audio-video-transcriber/scripts/install.sh
```

or:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

### A Large File Was Not Transcribed

The transcriber waits for file size to stabilize before starting. If a copy is interrupted, copy the file again or run single-file transcription manually.

### Chinese Recognition Is Poor

Try a larger model:

```bash
export AVT_MODEL="medium"
```

You can also force Chinese:

```bash
export AVT_LANGUAGE="Chinese"
```

### How Do I Change The Model?

```bash
export AVT_MODEL="medium"
```

or pass:

```bash
./bin/avt transcribe ~/Desktop/test.mp4 --model medium
```

### How Do I Change The Output Language?

```bash
export AVT_LANGUAGE="English"
```

For auto detection:

```bash
export AVT_LANGUAGE="auto"
```

### How Do I Stop Watching?

```bash
./skills/audio-video-transcriber/scripts/stop_watcher.sh
```

### How Do I View Logs?

```bash
./bin/avt status
```

Logs are stored in:

```text
~/AudioVideoTranscriber/logs
```

### macOS Permission Issues

If files on Desktop, Documents, or external drives cannot be read, grant Terminal or Codex permission in System Settings > Privacy & Security.

### Linux Permission Issues

Make sure the current user can read the input file and write to `AVT_BASE_DIR`.

### Windows / WSL

Windows users can use either WSL or native PowerShell. WSL is recommended when you want Unix-like shell behavior. Native Windows is supported through `.\bin\avt.ps1` and `scripts\*.ps1`. In all cases, install Python, Whisper, and ffmpeg and ensure they are available through the relevant environment or `PATH`.

## Security And Privacy

- Default processing is local.
- Audio and video files are not uploaded.
- No paid API is used.
- You can inspect every script in this repository.
- Scripts do not run `sudo`.
- Scripts do not modify shell startup files.

## Roadmap

- Batch transcription
- Speaker diarization
- Automatic meeting notes
- Automatic Xiaohongshu / WeChat article material generation
- Automatic highlight summaries
- Timestamp-based media slicing
- Graphical interface

## License

MIT License. See [LICENSE](LICENSE).

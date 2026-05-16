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
- Creates an original transcript plus `*.transcript.docx` by default.
- Progressively creates summary, correction, publish, and meeting-note deliverables only when requested.
- Optionally creates handoff-friendly HTML such as `*.summary.html`, `*.corrections.html`, `*.publish.html`, and `*.meeting-notes.html`.
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

## Natural Codex Examples

Most users do not need to know the CLI commands. In Codex, ask naturally:

```text
帮我转写这个音频：/Users/a26573/Desktop/test.m4a
```

```text
帮我转写这个音频，并整理成内容总结版：/Users/a26573/Desktop/test.m4a
```

```text
帮我把这个采访录音转写出来，再整理成刊物发布版：/Users/a26573/Desktop/interview.m4a
```

```text
帮我转写这个会议录音，并整理成会议纪要：/Users/a26573/Desktop/meeting.m4a
```

If you only ask for transcription, Codex should stop after the original transcript and `*.transcript.docx`, then offer to continue with a summary, correction pass, publishable article, meeting notes, or a cleaned verbatim transcript.

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
git clone https://github.com/luoxiluoye/audio-video-transcriber-skill.git
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

## Progressive Deliverables

Every successful transcription creates the original transcript next to the Whisper outputs:

```text
<name>.transcript.docx
```

`*.transcript.docx` is the complete transcript in a Word-friendly layout and can be viewed directly after transcription. It includes the source file name, generation time, transcript path, output formats, and paragraphs. When the input transcript has SRT/VTT/Whisper timestamps, the Word transcript preserves those time ranges.

By default, `transcribe` does not force summary, correction, publish, meeting-note, or HTML files. That keeps the first result simple for users who only asked for transcription.

When the user asks for extra整理, create only the requested deliverable:

```text
<name>.summary.md
<name>.summary.docx
<name>.summary.html
<name>.corrections.md
<name>.corrections.docx
<name>.corrections.html
<name>.publish.md
<name>.publish.docx
<name>.publish.html
<name>.meeting-notes.md
<name>.meeting-notes.docx
<name>.meeting-notes.html
```

Actual output files use the audio/video stem as a prefix; they are not bare filenames. For example, `avt-watch-test-10s.m4a` produces names such as:

```text
avt-watch-test-10s.transcript.docx
avt-watch-test-10s.summary.md
avt-watch-test-10s.summary.docx
avt-watch-test-10s.corrections.md
avt-watch-test-10s.corrections.docx
avt-watch-test-10s.publish.docx
```

Create only a content summary for an existing transcript:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind summary --all
```

Create only a correction/polishing draft:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind corrections --all
```

Create a publishable article draft:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind publish --all
```

Create meeting notes:

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind meeting-notes --all
```

`review` creates a structured Markdown draft and matching Word/HTML shells. Codex should read the transcript, fill the Markdown with real content, then run `review-sync` so the final Word/HTML reflects the completed Markdown.

After Codex or another agent fills the Markdown files, sync the final content to Word and HTML:

```bash
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.summary.md
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.corrections.md
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.publish.md
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.meeting-notes.md
```

Or sync every existing sibling Markdown file from the transcript path:

```bash
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.txt --all
```

`review-sync` overwrites the matching DOCX/HTML files so they reflect the latest Markdown content.

After `review-sync`, the synced DOCX/HTML files are the final deliverables because they are rendered from the completed Markdown.

Skip transcript Word generation for one transcription:

```bash
./bin/avt transcribe ~/Desktop/test.mp4 --no-review
```

Overwrite existing generated files:

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
2. If the user only asked for transcription, deliver `test.transcript.docx` and offer next-step整理 options.
3. If the user asked for a summary, correction pass, publishable article, or meeting notes, let the agent read `~/AudioVideoTranscriber/output/test.txt`.
4. Create only the requested Markdown kind, fill it, then run `./bin/avt review-sync ~/AudioVideoTranscriber/output/test.txt --all`.
5. Deliver the requested final DOCX/HTML files and explain their intended use in plain language.

If the user asks an Agent to "transcribe and summarize", "转写并总结", "精修", "刊物发布版", or "会议纪要", the Agent should complete the requested整理 in one flow instead of stopping after the Markdown shell is created.

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

The default output folder contains Whisper outputs such as `json`, `srt`, `tsv`, `txt`, and `vtt`, plus `*.transcript.docx`. Requested extra versions appear beside them, for example `*.summary.docx`, `*.corrections.docx`, `*.publish.docx`, or `*.meeting-notes.docx`.

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

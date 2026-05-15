---
name: audio-video-transcriber
description: Use this skill when the user wants to transcribe local audio or video into text/subtitles, create SRT/VTT subtitles, process meeting recordings, interview recordings, or start a local inbox watcher workflow. Trigger words include transcribe, transcription, audio to text, video to text, whisper, subtitle, srt, vtt, meeting notes, 录音转文字, 视频转文字, 自动转写, 字幕, 会议录音, 访谈录音。
---

# Audio Video Transcriber

Use this skill to transcribe local audio or video files with a local Whisper CLI. It never uploads media files, never calls a cloud API by default, and never installs dependencies unless the user explicitly asks.

## Core Rules

- Do local transcription only. Do not upload audio or video files.
- Default to the user's existing `whisper` CLI.
- Do not hard-code user-specific paths.
- Do not commit or generate Whisper models, ffmpeg binaries, audio files, video files, or transcription outputs into this repository.
- Do not use paid APIs.
- Do not run `sudo`.
- Do not edit shell startup files such as `~/.zshrc` or `~/.bashrc` unless the user explicitly agrees.
- If system dependencies are missing, show commands for the user to run instead of installing them automatically.

## Configuration

Read configuration from environment variables first:

- `AVT_WHISPER_BIN`: path to the Whisper CLI
- `AVT_PYTHON_BIN`: Python interpreter for watcher scripts
- `AVT_BASE_DIR`: working directory for inbox/output/done/logs
- `AVT_MODEL`: Whisper model name
- `AVT_LANGUAGE`: transcription language
- `AVT_VENV_DIR`: local virtual environment path

If `AVT_WHISPER_BIN` is not set, try `which whisper`. If Whisper still cannot be found, guide the user to run:

```bash
./skills/audio-video-transcriber/scripts/doctor.sh
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

Defaults:

- Base dir: `~/AudioVideoTranscriber`
- Inbox: `~/AudioVideoTranscriber/inbox`
- Output: `~/AudioVideoTranscriber/output`
- Done: `~/AudioVideoTranscriber/done`
- Logs: `~/AudioVideoTranscriber/logs`
- Model: `small`
- Language: `Chinese`
- Output format: `all`
- Review pack: enabled by default, creates `*.transcript.docx`, `*.summary.md`, `*.summary.docx`, `*.corrections.md`, and `*.corrections.docx`
- Optional review HTML: use `--html` or `--all` to create `*.summary.html` and `*.corrections.html`

Supported extensions: `mp3`, `wav`, `m4a`, `aac`, `flac`, `mp4`, `mov`, `mkv`, `avi`, `webm`.

If the user asks for English, pass `--language English`. If the user asks for automatic language detection, use `--language auto`, which makes `transcribe.py` omit Whisper's `--language` argument.

## Command Routing

When the user asks to transcribe a specific file, call:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4"
```

After transcription, the script creates a local post-transcription review pack beside the Whisper outputs:

- `*.transcript.docx`: complete transcript deliverable with title, source file name, generation time, transcript path, output format list, paragraphs, and timestamps when available.
- `*.summary.md` and `*.summary.docx`: content-summary deliverables with core summary, key content, key viewpoints, action items, timeline, data and information analysis, and highlight summary.
- `*.corrections.md` and `*.corrections.docx`: correction deliverables with likely recognition errors, proper noun normalization, sentence polishing notes, and corrected text.
- `*.summary.html` and `*.corrections.html`: optional standalone HTML deliverables when the user asks for HTML or all formats.

The local scripts generate structured templates and Word/HTML shells. They do not call an LLM and do not pretend the summary/corrections are finished. If the user asks to "transcribe and summarize", "整理", "精修", or "生成纪要", the agent must continue after transcription:

1. Read the transcript output.
2. Fill `*.summary.md` with a real summary, including data and information analysis when numbers, dates, money, percentages, rankings, comparison, growth/decline, business metrics, or task milestones appear.
3. Fill `*.corrections.md` with likely ASR mistakes, proper nouns, sentence polish notes, and corrected text.
4. Regenerate or update `*.summary.docx` and `*.corrections.docx`; generate/update HTML too when useful or requested.
5. Tell the user where every output file is and which file is best for direct delivery.

Do not rerun `postprocess.py --overwrite` after manually filling the summary/corrections unless you intend to reset the deliverables back to templates. When converting filled Markdown into Word/HTML, preserve the completed content.

If no local LLM API or capable agent is available, do not fail; leave the templates for a later agent pass. Do not upload transcripts or media files.

When the user asks to create or refresh the review pack for an existing transcript, call:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt"
```

For HTML deliverables, call:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --html
```

For all review formats, call:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --all
```

When the user asks to start automatic transcription or watch an inbox folder, call:

```bash
./skills/audio-video-transcriber/scripts/start_watcher.sh
```

When the user asks to stop automatic transcription, call:

```bash
./skills/audio-video-transcriber/scripts/stop_watcher.sh
```

When the user asks for status or logs, call:

```bash
./skills/audio-video-transcriber/scripts/status.sh
```

When the user says "whisper not found", "没有 whisper", "帮我配置转写环境", or "初始化转写环境", call environment detection first:

```bash
./skills/audio-video-transcriber/scripts/doctor.sh
```

When the user explicitly asks to install Whisper, call:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

When the user asks for one-step initialization, call:

```bash
./skills/audio-video-transcriber/scripts/bootstrap.sh --yes
```

## Common Commands

Environment check:

```bash
./skills/audio-video-transcriber/scripts/doctor.sh
```

One-step initialization:

```bash
./skills/audio-video-transcriber/scripts/bootstrap.sh --yes
```

Install local Whisper environment:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

Single-file transcription:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4"
```

Create review deliverables for an existing transcript:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt"
```

Create review deliverables with HTML:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --html
```

Skip review-pack generation for one transcription:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --no-review
```

Start inbox watcher:

```bash
./skills/audio-video-transcriber/scripts/start_watcher.sh
```

Stop inbox watcher:

```bash
./skills/audio-video-transcriber/scripts/stop_watcher.sh
```

Check status:

```bash
./skills/audio-video-transcriber/scripts/status.sh
```

For detailed usage and troubleshooting, read `references/usage.md` only when more examples are needed.

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
- Treat transcription and editorial整理 as progressive deliverables. Do not create summaries, corrections, HTML, publish drafts, or meeting notes unless the user asks for that extra整理.

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
- Whisper output format: `all`
- Default Codex delivery: original transcript plus `*.transcript.docx`

Supported extensions: `mp3`, `wav`, `m4a`, `aac`, `flac`, `mp4`, `mov`, `mkv`, `avi`, `webm`.

If the user asks for English, pass `--language English`. If the user asks for automatic language detection, use `--language auto`, which makes `transcribe.py` omit Whisper's `--language` argument.

## Progressive Workflow

### 1. User only asks to transcribe

When the user says something like:

```text
帮我转写这个音频：/path/to/audio.m4a
```

Do this:

1. Check the environment with `doctor.sh`.
2. Transcribe the file.
3. Generate the raw transcript and `*.transcript.docx`.
4. Stop there unless the user asked for extra整理.
5. Reply in plain language:

```text
我已完成原始转写稿，文件在……。这版保留了口语表达和原始顺序。
如果需要，我还可以继续整理成：内容总结版、勘误精修版、刊物发布版、会议纪要版或逐字稿清洁版。
```

Command:

```bash
./skills/audio-video-transcriber/scripts/doctor.sh
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/audio.m4a"
```

Do not automatically generate `summary`, `corrections`, `publish`, `meeting-notes`, or HTML for this default case.

### 2. User asks for summary or key points

Trigger words include: `总结`, `内容总结`, `提炼`, `要点`, `快速浏览`, `汇报`.

After transcription:

1. Read the transcript.
2. Create and fill `*.summary.md` with a real content summary.
3. Sync it to `*.summary.docx` and `*.summary.html`.
4. Tell the user this is the "内容总结版", suitable for quick reading and reporting.

Use:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind summary --all
```

Then fill `*.summary.md` yourself from the transcript and sync:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --sync --all
```

### 3. User asks for correction or a smoother transcript

Trigger words include: `精修`, `勘误`, `纠错`, `通顺`, `整理成通顺版本`, `清洁版`.

After transcription:

1. Read the transcript.
2. Create and fill `*.corrections.md`.
3. Fix common口误, repeated words, typos, and obvious ASR errors.
4. Preserve the original meaning and avoid over-rewriting.
5. Sync to `*.corrections.docx` and `*.corrections.html`.
6. Tell the user this is the "勘误精修版", suitable for comparing against the original transcript.

Use:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind corrections --all
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --sync --all
```

### 4. User asks for a publishable article

Trigger words include: `刊物版`, `公众号版`, `发布版`, `可发布稿`, `可读稿`, `文章`.

After transcription:

1. Read the transcript.
2. Create and fill `*.publish.md`.
3. Turn the transcript into a natural, coherent article with paragraphs.
4. Preserve the speaker's core viewpoints.
5. Add light transitions only when needed. Do not invent facts.
6. Sync to `*.publish.docx` and `*.publish.html`.
7. Tell the user this is the "刊物发布版", suitable for human review before publication.

Use:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind publish --all
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --sync --all
```

### 5. User asks for meeting notes or a report version

Trigger words include: `会议纪要`, `纪要`, `汇报版`, `汇报材料`, `待办事项`, `后续动作`.

After transcription:

1. Read the transcript.
2. Create and fill `*.meeting-notes.md`.
3. Extract the meeting topic, core viewpoints, action items, risks, and next steps.
4. Sync to `*.meeting-notes.docx` and `*.meeting-notes.html`.
5. Tell the user this is the "会议纪要版".

Use:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind meeting-notes --all
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --sync --all
```

## File Naming

Actual output files use the source media stem as a prefix. They are not bare names.

Examples for `/path/to/avt-watch-test-10s.m4a`:

- `avt-watch-test-10s.txt`
- `avt-watch-test-10s.transcript.docx`
- `avt-watch-test-10s.summary.md`
- `avt-watch-test-10s.summary.docx`
- `avt-watch-test-10s.summary.html`
- `avt-watch-test-10s.corrections.md`
- `avt-watch-test-10s.corrections.docx`
- `avt-watch-test-10s.corrections.html`
- `avt-watch-test-10s.publish.md`
- `avt-watch-test-10s.publish.docx`
- `avt-watch-test-10s.publish.html`
- `avt-watch-test-10s.meeting-notes.md`
- `avt-watch-test-10s.meeting-notes.docx`
- `avt-watch-test-10s.meeting-notes.html`

## Command Routing

When the user asks to transcribe a specific file, call:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4"
```

When the user asks to create or refresh editorial deliverables for an existing transcript, call:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind summary --all
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind corrections --all
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind publish --all
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind meeting-notes --all
```

When the user or agent has completed the Markdown, sync the finished Markdown to DOCX/HTML:

```bash
./bin/avt review-sync "/path/to/transcript.txt" --all
```

or:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --sync --all
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

For detailed usage and troubleshooting, read `references/usage.md` only when more examples are needed.

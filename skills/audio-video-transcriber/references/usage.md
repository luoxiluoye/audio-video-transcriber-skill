# Audio Video Transcriber Usage

This reference gives examples for using the Codex skill and bundled scripts.

## Codex Examples

```text
Use $audio-video-transcriber to transcribe ~/Desktop/interview.mp4
```

```text
Use $audio-video-transcriber to start an automatic transcription inbox.
```

```text
Use $audio-video-transcriber to check my Whisper transcription setup.
```

```text
Use $audio-video-transcriber to stop automatic transcription.
```

## Single File Transcription

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4"
```

With a custom model:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --model medium
```

With a custom language:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --language English
```

With automatic language detection:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --language auto
```

With a custom output directory:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --output-dir "$HOME/transcripts"
```

Skip the review pack:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --no-review
```

Move the source file to `done` after success:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --move-done
```

## Post-Transcription Review Pack

By default, each transcription creates:

```text
<name>.transcript.docx
<name>.summary.md
<name>.summary.docx
<name>.corrections.md
<name>.corrections.docx
```

The transcript Word file is a complete transcript deliverable. The summary files ask an agent to fill in core summary, key content, key viewpoints, action items, timeline, data and information analysis, and highlight summary. The corrections files ask an agent to identify likely recognition errors, normalize proper nouns, explain sentence polishing, and produce corrected text.

If no local LLM API or capable agent is available, these files are still useful structured templates. They contain the transcript path and clear task instructions.

Create or refresh the review pack for an existing transcript:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --overwrite
```

Generate standalone HTML too:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --html
```

Generate every supported review format:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --all
```

Keep Markdown only:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --markdown-only
```

## Automatic Inbox Watcher

Start:

```bash
./skills/audio-video-transcriber/scripts/start_watcher.sh
```

Drop supported files into:

```text
~/AudioVideoTranscriber/inbox
```

Stop:

```bash
./skills/audio-video-transcriber/scripts/stop_watcher.sh
```

Status and logs:

```bash
./skills/audio-video-transcriber/scripts/status.sh
```

## Custom Model

Use an environment variable:

```bash
export AVT_MODEL="medium"
```

or pass an argument:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --model medium
```

## Custom Language

Chinese:

```bash
export AVT_LANGUAGE="Chinese"
```

English:

```bash
export AVT_LANGUAGE="English"
```

Automatic detection:

```bash
export AVT_LANGUAGE="auto"
```

## Custom Directories

Set a base directory:

```bash
export AVT_BASE_DIR="$HOME/AudioVideoTranscriber"
```

The scripts create these folders under it:

```text
inbox/
output/
done/
logs/
```

Set only the output directory for one command:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --output-dir "$HOME/transcripts"
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

## Troubleshooting

### Whisper CLI not found

Run:

```bash
./skills/audio-video-transcriber/scripts/doctor.sh
```

Then install a local environment if needed:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

or set:

```bash
export AVT_WHISPER_BIN="/path/to/whisper"
```

### ffmpeg not found

macOS:

```bash
brew install ffmpeg
```

Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y ffmpeg
```

Windows:

Install ffmpeg and add it to `PATH`.

### watchdog not found

Run:

```bash
./skills/audio-video-transcriber/scripts/install.sh
```

or:

```bash
./skills/audio-video-transcriber/scripts/install_whisper.sh
```

### Large files do not start immediately

The transcriber waits until file size is stable to avoid processing half-copied files. Wait for copying to finish, or run with:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --no-wait
```

### Output already exists

If `output/<basename>.txt` already exists, transcription is skipped to avoid duplicate work. Delete or move the old output if you want to re-run.

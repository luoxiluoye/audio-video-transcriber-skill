# Audio Video Transcriber Usage

This reference gives examples for using the Codex skill and bundled scripts.

## Codex Examples

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

Skip the transcript Word file:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --no-review
```

Move the source file to `done` after success:

```bash
python3 skills/audio-video-transcriber/scripts/transcribe.py "/path/to/file.mp4" --move-done
```

## Progressive Deliverables

By default, each transcription creates the raw transcript and:

```text
<name>.transcript.docx
```

The transcript Word file is a complete transcript deliverable. Summary, correction, publish, meeting-note, and HTML files are created only when the user asks for those extra versions.

Output files use the media stem as a prefix, for example `avt-watch-test-10s.summary.docx`, not a bare `summary.docx`.

Create a content summary:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind summary --all
```

Create a correction/polishing version:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind corrections --all
```

Create a publishable article draft:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind publish --all
```

Create meeting notes:

```bash
python3 skills/audio-video-transcriber/scripts/postprocess.py "/path/to/transcript.txt" --kind meeting-notes --all
```

After a user or agent edits the generated Markdown, sync finished Markdown files to final Word/HTML:

```bash
./bin/avt review-sync "/path/to/transcript.txt" --all
```

Sync just one edited Markdown file:

```bash
./bin/avt review-sync "/path/to/transcript.summary.md"
./bin/avt review-sync "/path/to/transcript.corrections.md"
./bin/avt review-sync "/path/to/transcript.publish.md"
./bin/avt review-sync "/path/to/transcript.meeting-notes.md"
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

# Audio Video Transcriber Skill

一个本地音视频转写 + Codex/Agent 智能整理工具。可以把音频/视频转成文字，并按需生成 Word/HTML 格式的总结稿、会议纪要、刊物版和勘误精修版。

这个项目默认使用本地 Whisper 转写，不上传音频/视频，不默认调用云端 API。普通用户可以直接把音频路径发给 Codex，让它完成转写和后续整理。

## 它能做什么

- 把音频或视频转成文字稿、字幕和 Whisper 原始输出。
- 默认生成原始转写稿和 Word 版全文稿。
- 按需整理成内容总结版、会议纪要版、刊物发布版、勘误精修版。
- 输出 Markdown、Word 和 HTML，方便继续编辑、汇报、发布或粘贴到文档工具。
- 支持单文件转写，也支持监听 inbox 文件夹自动处理。
- 本地处理，适合不想把录音上传到第三方服务的场景。

支持格式：`mp3`、`wav`、`m4a`、`aac`、`flac`、`mp4`、`mov`、`mkv`、`avi`、`webm`。

## 适合谁使用

- 内容运营：把访谈、播客、视频素材整理成可读稿或发布稿。
- 会议参与者：把会议录音整理成纪要、待办和风险点。
- 采访者和研究者：把录音转成可检索的文字，并做初步勘误。
- 课程、讲座、播客制作者：生成转写稿和字幕素材。
- 使用 Codex 或其他 Agent 的用户：希望用自然语言完成转写和整理，不想手动敲一串命令。

## 最简单用法：直接让 Codex 帮你处理

安装好 Skill 后，你可以像这样对 Codex 说：

```text
帮我转写这个音频：/Users/xxx/Desktop/test.m4a
```

```text
帮我转写这个会议录音，并整理成会议纪要：/Users/xxx/Desktop/meeting.m4a
```

```text
帮我把这个采访录音转写出来，再整理成刊物发布版：/Users/xxx/Desktop/interview.m4a
```

```text
帮我转写这个音频，并整理成内容总结版：/Users/xxx/Desktop/test.m4a
```

如果你只说“转写”，Codex 会先交付原始转写稿。它不会默认强制生成总结、勘误、HTML 或发布稿。你之后可以继续说“再帮我总结一下”“整理成会议纪要”“精修成通顺版本”。

## 安装方式

推荐方式是 clone 完整仓库，然后把 Skill 安装到用户级 Codex skills 目录。

```bash
git clone https://github.com/luoxiluoye/audio-video-transcriber-skill.git
cd audio-video-transcriber-skill
```

安装 Skill：

```bash
mkdir -p ~/.agents/skills
cp -R skills/audio-video-transcriber ~/.agents/skills/
```

检查本地环境：

```bash
./bin/avt doctor
```

如果已经安装了 Whisper，但缺少 watcher 或 Word 输出依赖：

```bash
./skills/audio-video-transcriber/scripts/install.sh
```

如果还没有 Whisper，可以运行本地初始化脚本：

```bash
./bin/avt bootstrap
```

初始化脚本不会运行 `sudo`，也不会自动修改 shell 启动文件。

## 输出文件说明

输出文件都会带原音频/视频文件名前缀，不会使用裸文件名。

例如输入文件是：

```text
/Users/xxx/Desktop/test.m4a
```

常见输出会是：

```text
test.txt
test.srt
test.vtt
test.json
test.tsv
test.transcript.docx
test.summary.md
test.summary.docx
test.summary.html
test.publish.md
test.publish.docx
test.publish.html
test.meeting-notes.md
test.meeting-notes.docx
test.meeting-notes.html
test.corrections.md
test.corrections.docx
test.corrections.html
```

也就是说，文件名会是 `test.transcript.docx`、`test.summary.docx`，不是 `transcript.docx` 或 `summary.docx`。

默认转写只会生成 Whisper 输出、`test.txt` 和 `test.transcript.docx`。其他整理稿只在用户明确要求时生成。

默认输出目录是：

```text
~/AudioVideoTranscriber/output
```

## 支持的交付类型

| 用户说法 | 生成内容 | 输出文件 |
| --- | --- | --- |
| 只转写 | 完整转写稿 | `*.txt` / `*.transcript.docx` |
| 转写并总结 | 内容总结版 | `*.summary.md/docx/html` |
| 转写并整理成会议纪要 | 会议纪要 | `*.meeting-notes.md/docx/html` |
| 转写并整理成刊物版 | 刊物发布稿 | `*.publish.md/docx/html` |
| 转写并勘误/精修 | 勘误精修版 | `*.corrections.md/docx/html` |

### 原始转写稿

保留口语表达和原始顺序，适合做备份、回听核对和后续整理。

### 内容总结版

提炼核心摘要、重点内容、关键观点、待办事项和风险疑点，适合快速浏览和汇报。

### 会议纪要版

提炼会议主题、核心观点、待办事项、风险点和后续动作，适合会后同步。

### 刊物发布版

把转写内容整理成自然、连贯、有段落结构的可读稿。可以轻度补充衔接语，但不能编造事实。适合进一步人工审校后发布。

### 勘误精修版

修正常见口误、重复词、错别字和明显语音识别错误，同时保留原意，适合对照原始转写稿使用。

## 命令行用法

虽然推荐在 Codex 里用自然语言操作，但这个项目也可以直接用命令行。

检查环境：

```bash
./bin/avt doctor
```

转写单个文件：

```bash
./bin/avt transcribe ~/Desktop/test.m4a
```

指定模型或语言：

```bash
./bin/avt transcribe ~/Desktop/test.m4a --model small --language Chinese
./bin/avt transcribe ~/Desktop/test.m4a --language auto
```

为已有 transcript 生成内容总结：

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind summary --all
```

生成刊物发布版：

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind publish --all
```

生成会议纪要：

```bash
./bin/avt review ~/AudioVideoTranscriber/output/test.txt --kind meeting-notes --all
```

当 Codex 或用户补全 Markdown 后，同步生成最终 Word/HTML：

```bash
./bin/avt review-sync ~/AudioVideoTranscriber/output/test.txt --all
```

启动自动监听文件夹：

```bash
./bin/avt watch
open ~/AudioVideoTranscriber/inbox
```

停止监听：

```bash
./bin/avt stop
```

查看状态和日志：

```bash
./bin/avt status
```

## Codex Skill 用法

Skill 文件位于：

```text
skills/audio-video-transcriber/SKILL.md
```

安装到用户级 Skill 目录后，Codex 会在你提出转写、字幕、会议纪要、采访整理等请求时使用它。

```bash
mkdir -p ~/.agents/skills
cp -R skills/audio-video-transcriber ~/.agents/skills/
```

安装后可以直接说：

```text
帮我转写这个音频：/Users/xxx/Desktop/test.m4a
```

或者明确指定：

```text
Use $audio-video-transcriber to transcribe /Users/xxx/Desktop/test.m4a
```

Skill 的默认工作流是渐进式交付：

1. 只要求转写时，只生成原始转写稿和 Word 全文稿。
2. 要求总结时，再生成内容总结版。
3. 要求精修时，再生成勘误精修版。
4. 要求发布稿时，再生成刊物发布版。
5. 要求会议纪要时，再生成会议纪要版。

## 高级用法

### Standalone CLI

不使用 Codex 也可以运行：

```bash
./bin/avt doctor
./bin/avt transcribe ~/Desktop/test.m4a
./bin/avt status
```

Windows PowerShell 支持：

```powershell
.\bin\avt.ps1 doctor
.\bin\avt.ps1 transcribe "$env:USERPROFILE\Desktop\test.m4a"
.\bin\avt.ps1 status
```

### MCP Server

仓库包含可选 MCP server，适合接入支持 MCP 的 Agent 或编辑器。

参考文件：

```text
.mcp.json
mcp/README.md
mcp/server.py
```

可用工具包括：

- `transcribe_file`
- `postprocess_transcript`
- `start_watcher`
- `stop_watcher`
- `status`
- `doctor`
- `bootstrap`

### 自动 inbox watcher

Watcher 会监听：

```text
~/AudioVideoTranscriber/inbox
```

把音频或视频文件放进去后，脚本会自动转写，输出到：

```text
~/AudioVideoTranscriber/output
```

处理完成的源文件会移动到：

```text
~/AudioVideoTranscriber/done
```

## 常见问题

### Whisper not found

先检查环境：

```bash
./bin/avt doctor
```

如果需要安装本地 Whisper 环境：

```bash
./bin/avt bootstrap
```

也可以手动指定 Whisper 路径：

```bash
export AVT_WHISPER_BIN="/path/to/whisper"
```

### ffmpeg not found

Whisper 需要 `ffmpeg` 读取常见音视频文件。

macOS：

```bash
brew install ffmpeg
```

Ubuntu/Debian：

```bash
sudo apt update && sudo apt install -y ffmpeg
```

Windows：安装 ffmpeg，并把它加入 `PATH`。

### 第一次转写很慢

第一次运行 Whisper 模型时，Whisper 可能会下载模型到本地缓存。后续同模型转写通常会更快。

### 中文识别效果不好

可以尝试更大的模型：

```bash
./bin/avt transcribe ~/Desktop/test.m4a --model medium
```

也可以强制中文：

```bash
./bin/avt transcribe ~/Desktop/test.m4a --language Chinese
```

### 想自动识别语言

```bash
./bin/avt transcribe ~/Desktop/test.m4a --language auto
```

### macOS 无法读取桌面或文档里的文件

请到系统设置里给 Terminal 或 Codex 授权：System Settings > Privacy & Security。

### 这个项目会上传我的录音吗？

默认不会。转写在本地执行，不上传音频/视频，不默认调用付费 API。

## 项目结构

```text
.
├── bin/
│   ├── avt
│   └── avt.ps1
├── skills/
│   └── audio-video-transcriber/
│       ├── SKILL.md
│       ├── references/
│       └── scripts/
├── mcp/
│   ├── README.md
│   └── server.py
├── tests/
├── .codex-plugin/
└── README.md
```

## 隐私和安全

- 默认本地处理，不上传媒体文件。
- 不默认使用付费 API。
- 不提交 Whisper 模型、音频、视频或转写输出。
- 安装脚本不运行 `sudo`。
- 安装脚本不自动修改 shell 启动文件。

## License

MIT License. See [LICENSE](LICENSE).

#!/usr/bin/env python3
"""Create agent-ready summary and correction files for a transcript."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_BASE_DIR = Path("~/AudioVideoTranscriber").expanduser()


def expand_path(value: str | Path) -> Path:
    return Path(value).expanduser()


def default_output_dir() -> Path:
    base_dir = expand_path(os.environ.get("AVT_BASE_DIR", str(DEFAULT_BASE_DIR)))
    return base_dir / "output"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def read_transcript(path: Path) -> str:
    raw_text = read_text(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            return clean_transcript(raw_text)
        if isinstance(data, dict):
            if isinstance(data.get("text"), str):
                return data["text"].strip()
            segments = data.get("segments")
            if isinstance(segments, list):
                segment_text = [
                    str(segment.get("text", "")).strip()
                    for segment in segments
                    if isinstance(segment, dict) and segment.get("text")
                ]
                return "\n".join(segment_text).strip()
        return clean_transcript(raw_text)
    if suffix == ".tsv":
        rows = csv.DictReader(raw_text.splitlines(), delimiter="\t")
        if rows.fieldnames and "text" in rows.fieldnames:
            text_rows = [row.get("text", "").strip() for row in rows if row.get("text")]
            return "\n".join(text_rows).strip()
        lines = []
        for line in raw_text.splitlines():
            parts = line.split("\t")
            if parts and parts[-1].strip().lower() != "text":
                lines.append(parts[-1].strip())
        return "\n".join(line for line in lines if line).strip()
    return clean_transcript(raw_text)


def clean_transcript(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if "-->" in line:
            continue
        if line.upper() == "WEBVTT":
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def preview_chunks(text: str, max_chunks: int = 8, chunk_chars: int = 240) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    chunks = []
    for start in range(0, min(len(normalized), max_chunks * chunk_chars), chunk_chars):
        chunk = normalized[start : start + chunk_chars].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def word_count_rough(text: str) -> int:
    ascii_words = re.findall(r"[A-Za-z0-9_]+", text)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", text)
    return len(ascii_words) + len(cjk_chars)


def write_if_needed(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def build_summary(transcript_path: Path, source_file: str, transcript: str, generated_at: str) -> str:
    chunks = preview_chunks(transcript)
    chunk_lines = "\n".join(f"{idx}. {chunk}" for idx, chunk in enumerate(chunks, 1))
    if not chunk_lines:
        chunk_lines = "1. Transcript is empty or could not be parsed."

    return f"""# 内容总结

Source media: `{source_file or "unknown"}`

Transcript: `{transcript_path}`

Generated at: {generated_at}

> Agent task: read the transcript at the path above and replace the draft sections with a polished Chinese summary. If no local LLM API is available, keep this as the handoff template for a future agent pass.

## 核心信息

待 agent 精修：用 1-3 句话概括这段音频/视频最核心的信息。

## 重点观点

待 agent 精修：

- 提炼 5-10 条最重要观点。
- 合并重复表达。
- 保留关键名词、人名、地名、产品名、数据和结论。

## 时间线

待 agent 精修：按出现顺序列出关键事件、话题转换、时间点、决定和结论。

| 时间/顺序 | 内容 | 备注 |
| --- | --- | --- |
| 待 agent 核对 | 待 agent 填写 | - |

## 待办事项

待 agent 精修：如果转写中出现明确任务、承诺、负责人、时间点或下一步，请列在这里。

| 待办 | 负责人 | 截止时间 | 上下文 |
| --- | --- | --- | --- |
| 待 agent 核对 | 待 agent 填写 | 待 agent 填写 | 待 agent 填写 |

## 精华摘要

待 agent 精修：

- 重要观点：
- 重要例子：
- 可执行建议：
- 值得引用的表达：

## 风险与疑点

待 agent 精修：记录可能听错、逻辑跳跃、需要回听确认的地方。

## 转写线索预览

{chunk_lines}

## Transcript Stats

- Approximate length: {len(transcript)} characters
- Rough token/word signal: {word_count_rough(transcript)}
"""


def build_corrections(transcript_path: Path, source_file: str, transcript: str, generated_at: str) -> str:
    return f"""# 勘误与精修版

Source media: `{source_file or "unknown"}`

Transcript: `{transcript_path}`

Generated at: {generated_at}

> Agent task: read the transcript at the path above, identify likely ASR mistakes, and produce a corrected transcript. If no local LLM API is available, keep this as the handoff template for a future agent pass.

## 疑似错词

| 原句 | 疑似错词 | 建议修正 | 理由/上下文 | 置信度 |
| --- | --- | --- | --- | --- |
| 待 agent 核对 | 待 agent 填写 | 待 agent 填写 | 结合上下文判断 | - |

## 专有名词、人名、地名、机构名

| 原句 | 原转写 | 建议修正 | 类型 | 置信度 |
| --- | --- | --- | --- | --- |
| 待 agent 核对 | 待 agent 填写 | 待 agent 填写 | 人名/地名/机构名/品牌名/术语 | - |

## 勘误表

| 原句 | 建议修正 | 类型 | 理由/上下文 | 置信度 |
| --- | --- | --- | --- | --- |
| 待 agent 核对 | 待 agent 填写 | 错词/断句/数字/术语/重复 | 结合上下文判断 | - |

## 常见优先核对项

- 人名、公司名、品牌名、地名、楼盘/建筑名
- 英文缩写、产品名、技术词
- 数字、金额、百分比、年份、时间点
- 同音词、近音词、跨语言音译词
- Whisper 明显断句错误或重复片段

## 精修后的文本

待 agent 精修：在这里输出修正错别字、术语、断句和段落结构后的版本。保持原意，不要擅自添加转写中没有的信息。

## 原始转写

```text
{transcript}
```
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create summary and correction Markdown workspaces for a transcript."
    )
    parser.add_argument("transcript", help="Path to a transcript text file.")
    parser.add_argument("--source-file", default="", help="Original media file path.")
    parser.add_argument("--output-dir", default=None, help="Directory for Markdown outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing Markdown outputs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    transcript_path = expand_path(args.transcript)
    output_dir = expand_path(args.output_dir) if args.output_dir else default_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")
        transcript = read_transcript(transcript_path)
        stem = transcript_path.stem
        generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")

        summary_path = output_dir / f"{stem}.summary.md"
        corrections_path = output_dir / f"{stem}.corrections.md"

        summary_written = write_if_needed(
            summary_path,
            build_summary(transcript_path, args.source_file, transcript, generated_at),
            args.overwrite,
        )
        corrections_written = write_if_needed(
            corrections_path,
            build_corrections(transcript_path, args.source_file, transcript, generated_at),
            args.overwrite,
        )

        print("Post-processing files:")
        for path, written in (
            (summary_path, summary_written),
            (corrections_path, corrections_written),
        ):
            status = "created" if written else "exists"
            print(f"  {status}: {path}")
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should print friendly errors.
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

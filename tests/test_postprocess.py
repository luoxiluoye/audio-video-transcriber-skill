from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
POSTPROCESS_PATH = ROOT_DIR / "skills" / "audio-video-transcriber" / "scripts" / "postprocess.py"


def load_postprocess_module():
    spec = importlib.util.spec_from_file_location("avt_postprocess", POSTPROCESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {POSTPROCESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PostprocessTest(unittest.TestCase):
    def docx_text(self, path: Path) -> str:
        with zipfile.ZipFile(path) as package:
            return package.read("word/document.xml").decode("utf-8")

    def test_creates_markdown_and_word_templates(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "meeting.txt"
            output_dir = tmp_path / "out"
            transcript.write_text("我们讨论了项目计划。\n2026年5月15日收入增长20%，下周三之前完成初稿。\n", encoding="utf-8")

            result = module.main([str(transcript), "--output-dir", str(output_dir), "--source-file", "meeting.mp4"])

            self.assertEqual(result, 0)
            summary = (output_dir / "meeting.summary.md").read_text(encoding="utf-8")
            corrections = (output_dir / "meeting.corrections.md").read_text(encoding="utf-8")
            transcript_docx = output_dir / "meeting.transcript.docx"
            summary_docx = output_dir / "meeting.summary.docx"
            corrections_docx = output_dir / "meeting.corrections.docx"

            self.assertIn(f"Transcript: `{transcript}`", summary)
            self.assertIn("## 核心摘要", summary)
            self.assertIn("## 重点内容", summary)
            self.assertIn("## 关键观点", summary)
            self.assertIn("## 时间线", summary)
            self.assertIn("## 待办事项", summary)
            self.assertIn("## 数据与信息分析", summary)
            self.assertIn("## 精华版总结", summary)
            self.assertIn("Agent task:", summary)
            self.assertIn("收入增长20%", summary)

            self.assertIn(f"Transcript: `{transcript}`", corrections)
            self.assertIn("## 疑似识别错误表", corrections)
            self.assertIn("## 专有名词统一表", corrections)
            self.assertIn("## 语句精修说明", corrections)
            self.assertIn("## 精修后正文", corrections)
            self.assertIn("Agent task:", corrections)

            self.assertTrue(transcript_docx.exists())
            self.assertTrue(summary_docx.exists())
            self.assertTrue(corrections_docx.exists())
            self.assertIn("转写稿", self.docx_text(transcript_docx))
            self.assertIn("内容总结", self.docx_text(summary_docx))
            self.assertIn("数据与信息分析", self.docx_text(summary_docx))
            self.assertIn("勘误与精修版", self.docx_text(corrections_docx))

    def test_creates_html_outputs_when_requested(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "meeting.txt"
            output_dir = tmp_path / "out"
            transcript.write_text("第一段内容。\n第二段内容。", encoding="utf-8")

            result = module.main([str(transcript), "--output-dir", str(output_dir), "--html"])

            self.assertEqual(result, 0)
            summary_html = (output_dir / "meeting.summary.html").read_text(encoding="utf-8")
            corrections_html = (output_dir / "meeting.corrections.html").read_text(encoding="utf-8")
            self.assertIn("<style>", summary_html)
            self.assertIn("内容总结", summary_html)
            self.assertIn("数据与信息分析", summary_html)
            self.assertIn("勘误与精修版", corrections_html)
            self.assertIn("疑似识别错误表", corrections_html)

    def test_extracts_text_from_whisper_json(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "talk.json"
            transcript.write_text(
                '{"segments": [{"text": " 第一段 "}, {"text": "第二段"}]}',
                encoding="utf-8",
            )

            text = module.read_transcript(transcript)

            self.assertEqual(text, "第一段\n第二段")

    def test_extracts_timestamps_from_srt(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "clip.srt"
            transcript.write_text(
                "1\n00:00:01,000 --> 00:00:03,500\n第一段字幕。\n\n"
                "2\n00:00:04,000 --> 00:00:06,000\n第二段字幕。\n",
                encoding="utf-8",
            )

            segments = module.read_transcript_segments(transcript)

            self.assertEqual(segments[0].start, "00:00:01.000")
            self.assertEqual(segments[0].end, "00:00:03.500")
            self.assertEqual(segments[0].text, "第一段字幕。")

    def test_help_text_exposes_delivery_format_options(self) -> None:
        module = load_postprocess_module()
        help_text = module.build_parser().format_help()

        self.assertIn("--html", help_text)
        self.assertIn("--all", help_text)
        self.assertIn("--markdown-only", help_text)
        self.assertIn("--no-docx", help_text)


if __name__ == "__main__":
    unittest.main()

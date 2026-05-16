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
        self.assertIn("--sync", help_text)

    def test_syncs_completed_markdown_to_docx_and_html(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            summary = tmp_path / "meeting.summary.md"
            summary.write_text(
                "# 内容总结\n\n"
                "Transcript: `/tmp/meeting.txt`\n\n"
                "## 核心摘要\n\n"
                "这是已经由 Agent 补全的核心摘要。\n\n"
                "## 数据与信息分析\n\n"
                "| 数据/信息 | 原文位置或上下文 | 可能含义 | 备注 |\n"
                "| --- | --- | --- | --- |\n"
                "| 20% | 收入增长20% | 增长明显 | 已核对 |\n",
                encoding="utf-8",
            )

            result = module.main([str(summary), "--sync", "--all"])

            self.assertEqual(result, 0)
            synced_docx = tmp_path / "meeting.summary.docx"
            synced_html = tmp_path / "meeting.summary.html"
            self.assertTrue(synced_docx.exists())
            self.assertTrue(synced_html.exists())
            self.assertIn("已经由 Agent 补全", self.docx_text(synced_docx))
            self.assertIn("已经由 Agent 补全", synced_html.read_text(encoding="utf-8"))
            self.assertIn("收入增长20%", synced_html.read_text(encoding="utf-8"))

    def test_syncs_corrections_markdown_to_docx_and_html(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            corrections = tmp_path / "meeting.corrections.md"
            corrections.write_text(
                "# 勘误与精修版\n\n"
                "Transcript: `/tmp/meeting.txt`\n\n"
                "## 疑似识别错误表\n\n"
                "| 原句 | 疑似错词 | 建议修正 | 理由/上下文 | 置信度 |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| 原句内容 | 错词 | 正词 | 上下文支持 | 高 |\n\n"
                "## 精修后正文\n\n"
                "这是已经精修后的正文。\n",
                encoding="utf-8",
            )

            result = module.main([str(corrections), "--sync", "--all"])

            self.assertEqual(result, 0)
            synced_docx = tmp_path / "meeting.corrections.docx"
            synced_html = tmp_path / "meeting.corrections.html"
            self.assertTrue(synced_docx.exists())
            self.assertTrue(synced_html.exists())
            self.assertIn("已经精修后的正文", self.docx_text(synced_docx))
            self.assertIn("已经精修后的正文", synced_html.read_text(encoding="utf-8"))

    def test_sync_from_transcript_finds_sibling_markdown_files(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "meeting.txt"
            transcript.write_text("原始转写", encoding="utf-8")
            (tmp_path / "meeting.summary.md").write_text("# 内容总结\n\n已补全总结。", encoding="utf-8")
            (tmp_path / "meeting.corrections.md").write_text("# 勘误与精修版\n\n已补全勘误。", encoding="utf-8")

            result = module.main([str(transcript), "--sync", "--all"])

            self.assertEqual(result, 0)
            self.assertIn("已补全总结", self.docx_text(tmp_path / "meeting.summary.docx"))
            self.assertIn("已补全勘误", self.docx_text(tmp_path / "meeting.corrections.docx"))

    def test_missing_python_docx_does_not_block_markdown_or_html(self) -> None:
        module = load_postprocess_module()

        def missing_docx():
            raise RuntimeError("python-docx is missing for test")

        module.import_docx = missing_docx
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "meeting.txt"
            output_dir = tmp_path / "out"
            transcript.write_text("第一段内容。", encoding="utf-8")

            result = module.main([str(transcript), "--output-dir", str(output_dir), "--html"])

            self.assertEqual(result, 0)
            self.assertTrue((output_dir / "meeting.summary.md").exists())
            self.assertTrue((output_dir / "meeting.corrections.md").exists())
            self.assertTrue((output_dir / "meeting.summary.html").exists())
            self.assertTrue((output_dir / "meeting.corrections.html").exists())
            self.assertFalse((output_dir / "meeting.summary.docx").exists())

    def test_review_format_flags_control_outputs(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "meeting.txt"
            transcript.write_text("第一段内容。", encoding="utf-8")

            markdown_only_dir = tmp_path / "markdown-only"
            result = module.main([str(transcript), "--output-dir", str(markdown_only_dir), "--markdown-only"])
            self.assertEqual(result, 0)
            self.assertTrue((markdown_only_dir / "meeting.summary.md").exists())
            self.assertFalse((markdown_only_dir / "meeting.summary.docx").exists())
            self.assertFalse((markdown_only_dir / "meeting.summary.html").exists())

            html_only_dir = tmp_path / "html-only"
            result = module.main([str(transcript), "--output-dir", str(html_only_dir), "--html", "--no-docx"])
            self.assertEqual(result, 0)
            self.assertTrue((html_only_dir / "meeting.summary.md").exists())
            self.assertFalse((html_only_dir / "meeting.summary.docx").exists())
            self.assertTrue((html_only_dir / "meeting.summary.html").exists())

            all_dir = tmp_path / "all"
            result = module.main([str(transcript), "--output-dir", str(all_dir), "--all"])
            self.assertEqual(result, 0)
            self.assertTrue((all_dir / "meeting.summary.docx").exists())
            self.assertTrue((all_dir / "meeting.summary.html").exists())


if __name__ == "__main__":
    unittest.main()

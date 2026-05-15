from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
POSTPROCESS_PATH = ROOT_DIR / "skills" / "audio-video-transcriber" / "scripts" / "postprocess.py"


def load_postprocess_module():
    spec = importlib.util.spec_from_file_location("avt_postprocess", POSTPROCESS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {POSTPROCESS_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PostprocessTest(unittest.TestCase):
    def test_creates_summary_and_corrections_templates(self) -> None:
        module = load_postprocess_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            transcript = tmp_path / "meeting.txt"
            output_dir = tmp_path / "out"
            transcript.write_text("我们讨论了项目计划。\n下周三之前完成初稿。\n", encoding="utf-8")

            result = module.main([str(transcript), "--output-dir", str(output_dir), "--source-file", "meeting.mp4"])

            self.assertEqual(result, 0)
            summary = (output_dir / "meeting.summary.md").read_text(encoding="utf-8")
            corrections = (output_dir / "meeting.corrections.md").read_text(encoding="utf-8")

            self.assertIn(f"Transcript: `{transcript}`", summary)
            self.assertIn("## 核心信息", summary)
            self.assertIn("## 重点观点", summary)
            self.assertIn("## 时间线", summary)
            self.assertIn("## 待办事项", summary)
            self.assertIn("## 精华摘要", summary)
            self.assertIn("Agent task:", summary)

            self.assertIn(f"Transcript: `{transcript}`", corrections)
            self.assertIn("## 疑似错词", corrections)
            self.assertIn("## 专有名词、人名、地名、机构名", corrections)
            self.assertIn("## 精修后的文本", corrections)
            self.assertIn("Agent task:", corrections)

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


if __name__ == "__main__":
    unittest.main()

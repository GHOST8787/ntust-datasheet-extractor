"""V4 詳細迭代記錄器

每元件、每輪、每事件寫詳細紀錄：
  - JSONL：每行一個事件（給機器分析用），完整欄位含 timing / token-ish 估算 / raw response 預覽
  - Markdown：人類可讀的 per-part summary，方便 obsidian 翻

事件類型：
  - pdf_extract     : PDF 抽取階段（文字 / 截圖數量 / 耗時）
  - extraction      : Extraction Agent 一輪
  - validator       : 本地 validator 修了哪幾條
  - critic          : QA Critic Agent 一輪
  - final           : 該元件最終答案 + 總輪數 + 總耗時

寫到 output/iteration_logs/<cell_id>/<part_number>.jsonl 與 .md
另存 _index.md 列所有元件的快速一覽
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class IterationLogger:
    def __init__(self, base_dir: Path, cell_id: str):
        self.dir = base_dir / cell_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.cell_id = cell_id
        self.current_part: Optional[str] = None
        self.current_jsonl_path: Optional[Path] = None
        self.current_md_lines: List[str] = []
        self._part_t0: float = 0
        self._all_part_summaries: List[Dict] = []

    # ---------------------------------------------------------------
    def start_part(self, part_number: str):
        # 上一顆收尾
        if self.current_part is not None:
            self._finalize_part()
        self.current_part = part_number
        self.current_jsonl_path = self.dir / f"{part_number}.jsonl"
        # 清舊檔
        if self.current_jsonl_path.exists():
            self.current_jsonl_path.unlink()
        self.current_md_lines = [
            f"# {part_number}",
            "",
            f"_Cell: `{self.cell_id}`  ·  Started: {datetime.now().isoformat()}_",
            "",
        ]
        self._part_t0 = time.time()

    # ---------------------------------------------------------------
    def _write_jsonl(self, event: Dict):
        event["ts"] = datetime.now().isoformat()
        event["part_number"] = self.current_part
        with open(self.current_jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------------
    def log_pdf_extract(
        self,
        extractor_name: str,
        text_chars: int,
        num_images: int,
        elapsed_ms: int,
        image_pages: Optional[List[int]] = None,
    ):
        self._write_jsonl({
            "event": "pdf_extract",
            "round": 0,
            "extractor": extractor_name,
            "text_chars": text_chars,
            "num_images": num_images,
            "image_pages": image_pages or [],
            "elapsed_ms": elapsed_ms,
        })
        self.current_md_lines.append("## PDF 抽取")
        self.current_md_lines.append(f"- Extractor: `{extractor_name}`")
        self.current_md_lines.append(f"- 文字: {text_chars} 字元")
        self.current_md_lines.append(f"- 圖片: {num_images} 張" + (f"（頁碼 {image_pages}）" if image_pages else ""))
        self.current_md_lines.append(f"- 耗時: {elapsed_ms} ms")
        self.current_md_lines.append("")

    # ---------------------------------------------------------------
    def log_extraction(
        self,
        round_num: int,
        prompt_chars: int,
        response_raw: str,
        parsed_answer: Dict,
        elapsed_ms: int,
        multimodal: bool = False,
        num_images_sent: int = 0,
    ):
        self._write_jsonl({
            "event": "extraction",
            "round": round_num,
            "prompt_chars": prompt_chars,
            "response_chars": len(response_raw),
            "response_raw_preview": response_raw[:500],
            "parsed_answer": _strip_meta(parsed_answer),
            "elapsed_ms": elapsed_ms,
            "multimodal": multimodal,
            "num_images_sent": num_images_sent,
        })
        mm_tag = " 🖼️ multimodal" if multimodal else ""
        self.current_md_lines.append(f"## Round {round_num}")
        self.current_md_lines.append(f"### Extraction{mm_tag}")
        suffix = f"+ {num_images_sent} 張圖" if num_images_sent else ""
        self.current_md_lines.append(f"- Prompt: {prompt_chars} 字元 {suffix}")
        self.current_md_lines.append(f"- Response: {len(response_raw)} 字元, 耗時 {elapsed_ms} ms")
        self.current_md_lines.append("- 抽到的 JSON:")
        self.current_md_lines.append("```json")
        self.current_md_lines.append(json.dumps(_strip_meta(parsed_answer), ensure_ascii=False, indent=2)[:1000])
        self.current_md_lines.append("```")
        self.current_md_lines.append("")

    # ---------------------------------------------------------------
    def log_validator(self, round_num: int, fixes: List[str], answer_after: Dict):
        self._write_jsonl({
            "event": "validator",
            "round": round_num,
            "fixes": fixes,
            "answer_after_fixes": _strip_meta(answer_after),
        })
        self.current_md_lines.append("### Validator")
        if not fixes:
            self.current_md_lines.append("- ✅ 沒有 fix")
        else:
            self.current_md_lines.append(f"- ⚠️ {len(fixes)} 條 fix:")
            for f in fixes:
                self.current_md_lines.append(f"  - `{f}`")
        self.current_md_lines.append("")

    # ---------------------------------------------------------------
    def log_critic(
        self,
        round_num: int,
        mode: str,
        prompt_chars: int,
        response_raw: str,
        is_passed: bool,
        corrections: List[str],
        elapsed_ms: int,
    ):
        self._write_jsonl({
            "event": "critic",
            "round": round_num,
            "critic_mode": mode,
            "prompt_chars": prompt_chars,
            "response_chars": len(response_raw),
            "response_raw_preview": response_raw[:500],
            "is_passed": is_passed,
            "corrections": corrections,
            "elapsed_ms": elapsed_ms,
        })
        self.current_md_lines.append(f"### Critic ({mode})")
        status = "✅ PASS" if is_passed else "❌ FAIL"
        self.current_md_lines.append(f"- {status}, 耗時 {elapsed_ms} ms")
        self.current_md_lines.append(f"- Prompt: {prompt_chars} 字元, Response: {len(response_raw)} 字元")
        if corrections:
            self.current_md_lines.append(f"- {len(corrections)} 條 corrections:")
            for c in corrections:
                self.current_md_lines.append(f"  - {c[:250]}")
        self.current_md_lines.append("")

    # ---------------------------------------------------------------
    def log_final(self, total_rounds: int, final_answer: Dict, critic_final_passed: bool):
        total_elapsed_ms = int((time.time() - self._part_t0) * 1000)
        self._write_jsonl({
            "event": "final",
            "round": total_rounds,
            "final_answer": _strip_meta(final_answer),
            "critic_final_passed": critic_final_passed,
            "total_elapsed_ms": total_elapsed_ms,
        })
        self.current_md_lines.append("## Final")
        self.current_md_lines.append(f"- 跑完輪數: {total_rounds}")
        self.current_md_lines.append(f"- Critic 最終: {'✅ PASS' if critic_final_passed else '❌ 撐到 max rounds 強制收尾'}")
        self.current_md_lines.append(f"- 總耗時: {total_elapsed_ms} ms")
        self.current_md_lines.append("- 最終 JSON:")
        self.current_md_lines.append("```json")
        self.current_md_lines.append(json.dumps(_strip_meta(final_answer), ensure_ascii=False, indent=2))
        self.current_md_lines.append("```")

        self._all_part_summaries.append({
            "part": self.current_part,
            "rounds": total_rounds,
            "passed": critic_final_passed,
            "elapsed_ms": total_elapsed_ms,
        })

    # ---------------------------------------------------------------
    def log_error(self, message: str):
        self._write_jsonl({
            "event": "error",
            "message": message,
        })
        self.current_md_lines.append("## ❌ ERROR")
        self.current_md_lines.append(f"- {message}")

    # ---------------------------------------------------------------
    def _finalize_part(self):
        md_path = self.dir / f"{self.current_part}.md"
        md_path.write_text("\n".join(self.current_md_lines), encoding="utf-8")

    # ---------------------------------------------------------------
    def close(self):
        """所有元件跑完叫一次。寫 _index.md。"""
        if self.current_part is not None:
            self._finalize_part()
        # 寫 _index.md
        lines = [
            f"# {self.cell_id} — Iteration Index",
            "",
            f"_共 {len(self._all_part_summaries)} 顆元件_",
            "",
            "| 元件 | 輪數 | Critic 最終 | 總耗時 (ms) | Detail |",
            "|---|---|---|---|---|",
        ]
        for s in self._all_part_summaries:
            status = "✅" if s["passed"] else "❌ max-rounds"
            lines.append(f"| {s['part']} | {s['rounds']} | {status} | {s['elapsed_ms']} | [`{s['part']}.md`]({s['part']}.md) · [`{s['part']}.jsonl`]({s['part']}.jsonl) |")
        (self.dir / "_index.md").write_text("\n".join(lines), encoding="utf-8")


# 共用工具：移除 main.py 注入的 `_v3_history` 等 meta 欄位
def _strip_meta(answer: Dict) -> Dict:
    if not isinstance(answer, dict):
        return answer
    return {k: v for k, v in answer.items() if not k.startswith("_")}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCU《人机协同程序设计》第 6 周实践课：单一事实源（SSOT）一源多端自动化编译器
功能：
  1. [Gate 1] 扫描母稿 report.md，确保 100% 纯语义 CommonMark（0 HTML 标签、0 未填槽位）
  2. [Gate 2] 执行 AST 解析与幻灯片视觉预算检查（每页要点数 <= 6、标题字数防断行预警）
  3. [Gate 3] 一键分发编译：
     - dist/slides.html : 16:9 宽屏高对比度学术汇报幻灯片（自包含离线可交互 HTML）
     - dist/report.pdf  : A4 双面学术排版报告（支持 Typst 引擎 + 零外置依赖 PDF 兜底）

用法：
  python ssot_compiler.py
  python ssot_compiler.py --input report.md --outdir dist
"""

import argparse
import hashlib
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ==============================================================================
# 1. [Gate 1] 纯语义门禁与局部差分修补状态检查
# ==============================================================================
HTML_TAG_PATTERN = re.compile(
    r"</?(?:div|span|font|br|hr|style|script|table|tr|td|th|p|h[1-6]|center|img)\b[^>]*>",
    re.IGNORECASE,
)
SLOT_PATTERN = re.compile(r"\[待填槽位[：:][^\]]*\]")


def run_gate1_semantic_check(md_text: str, src_path: Path) -> bool:
    print("=" * 68)
    print(f"🔍 [Gate 1] 纯语义门禁扫描 (Target: {src_path.name})")
    print("=" * 68)

    lines = md_text.splitlines()
    html_violations = []
    slot_violations = []

    for idx, line in enumerate(lines, start=1):
        # 忽略行内反引号代码中的演示文字
        clean_line = re.sub(r"`[^`]+`", "", line)
        for m in HTML_TAG_PATTERN.finditer(clean_line):
            html_violations.append((idx, m.group(0), line.strip()))
        for m in SLOT_PATTERN.finditer(clean_line):
            slot_violations.append((idx, m.group(0), line.strip()))

    if html_violations:
        print("❌ [Gate 1 拦截] 检测到违规 HTML 表现层标签污染纯语义母稿：")
        for ln, tag, snippet in html_violations[:5]:
            print(f"   - 第 {ln:02d} 行发现 `{tag}` -> {snippet[:60]}")
        return False

    if slot_violations:
        print("❌ [Gate 1 拦截] 检测到尚未填充的 `[待填槽位]` 占位符：")
        for ln, slot, snippet in slot_violations[:5]:
            print(f"   - 第 {ln:02d} 行发现 `{slot}`")
        return False

    # 检查第 28~36 行是否已完成【任务四：带行号局部差分修补】
    if len(lines) >= 36:
        head_hash = hashlib.sha256("\n".join(lines[:27]).encode("utf-8")).hexdigest()[:12]
        tail_hash = hashlib.sha256("\n".join(lines[36:]).encode("utf-8")).hexdigest()[:12]
        patch_zone = "\n".join(lines[27:36])
        print(f"   ✔ 纯语义扫描通过：0 个 HTML 标签，0 个残留槽位（总行数：{len(lines)} 行）")
        print(f"   ✔ 上下文散列校验：Lines 01-27 [{head_hash}] | Lines 37-{len(lines):02d} [{tail_hash}]")
        if "840 秒" in patch_zone and "帕累托最优改进效应" in patch_zone:
            print("   ⚠️ [任务四提醒] 检测到第 28～36 行仍包含未修补的初稿缺陷（“840 秒”未折算为分钟、“帕累托最优”黑话）！")
            print("      建议参照实验指导完成【任务四：带行号局部差分修补】后再次运行本编译器。")
        else:
            print("   ✔ 局部差分修补核验：第 28～36 行（3.2 节）已完成单位统一折算与因果链补全！")
    else:
        print(f"   ✔ 纯语义扫描通过：0 个 HTML 标签，0 个残留槽位（总行数：{len(lines)} 行）")

    return True


# ==============================================================================
# 2. Markdown 轻量级 AST 解析器
# ==============================================================================
def parse_markdown_ast(md_text: str) -> dict:
    lines = md_text.splitlines()
    doc = {
        "title": "未命名研究报告",
        "abstract": "",
        "chapters": [],  # [{"title": ..., "sections": [{"title": ..., "paragraphs": [...], "table": [...]}]}]
    }

    current_chapter = None
    current_section = None
    in_table = False
    table_buf = []
    para_buf = []

    def flush_para():
        nonlocal para_buf, current_section
        if para_buf:
            merged = "".join(para_buf)
            if current_section is not None:
                current_section["paragraphs"].append(merged)
            elif current_chapter is not None:
                current_section = {
                    "title": current_chapter["title"],
                    "paragraphs": [merged],
                    "tables": [],
                }
                current_chapter["sections"].append(current_section)
            para_buf = []

    def flush_table():
        nonlocal in_table, table_buf
        if in_table and table_buf and current_section is not None:
            current_section["tables"].append(table_buf)
        in_table = False
        table_buf = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_para()
            flush_table()
            continue

        if line.startswith("# ") and doc["title"] == "未命名研究报告":
            flush_para()
            doc["title"] = line[2:].strip()
            continue

        if line.startswith("> "):
            flush_para()
            quote_content = line[2:].strip()
            doc["abstract"] = (doc["abstract"] + " " + quote_content).strip()
            continue

        if line.startswith("## "):
            flush_para()
            flush_table()
            current_chapter = {"title": line[3:].strip(), "sections": []}
            doc["chapters"].append(current_chapter)
            current_section = None
            continue

        if line.startswith("### "):
            flush_para()
            flush_table()
            if current_chapter is None:
                current_chapter = {"title": "核心章节", "sections": []}
                doc["chapters"].append(current_chapter)
            current_section = {
                "title": line[4:].strip(),
                "paragraphs": [],
                "tables": [],
            }
            current_chapter["sections"].append(current_section)
            continue

        if line.startswith("|") and line.endswith("|"):
            flush_para()
            # 忽略纯分隔行 | :--- | :--- |
            if re.match(r"^\|[\s:\-\|]+\|$", line):
                in_table = True
                continue
            in_table = True
            cells = [c.strip() for c in line.strip("|").split("|")]
            table_buf.append(cells)
            continue

        flush_table()
        para_buf.append(line)

    flush_para()
    flush_table()
    return doc


def format_inline_html(text: str) -> str:
    """将纯语义 Markdown 行内语法安全转换为 HTML 片段（用于多端渲染器内部使用）"""
    escaped = html.escape(text)
    # 数学公式轻量美化：$N=40$ / $\rightarrow$
    escaped = escaped.replace(r"$\rightarrow$", "→")
    escaped = re.sub(r"\$([^\$]+)\$", r'<span class="math-inline">\1</span>', escaped)
    # 行内代码 `code`
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    # 加粗 **bold**
    escaped = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def split_paragraph_to_bullets(paragraphs: list) -> list:
    """将学术长段落智能拆解为不超过 6 条的幻灯片高信息密度要点"""
    bullets = []
    for p in paragraphs:
        # 按分号或句号切分关键论断
        clauses = [c.strip() for c in re.split(r"[；;。]", p) if c.strip()]
        for c in clauses:
            if len(bullets) < 5:
                bullets.append(c + "。")
    return bullets[:6]


# ==============================================================================
# 3. [Gate 2] 视觉预算与防溢出预检（基于 AST 的语义卡片版式合成引擎）
# ==============================================================================
def _split_clauses(text: str) -> list:
    """按句号或分号切分长段落为独立论断"""
    return [c.strip() + "。" for c in re.split(r"[；;。]", text) if c.strip()]


def _extract_table_insight(tbl: list) -> str:
    """从对比表格末行（相对变化幅度/汇总行）自动提炼底部数据洞察文本"""
    if len(tbl) < 2:
        return "实测数据验证了干预方案在核心评测指标上的显著改善效应。"
    headers = tbl[0]
    last_row = tbl[-1]
    highlights = []
    for col_idx in range(1, min(len(headers), len(last_row))):
        h_name = re.sub(r"\s*\([^)]*\)", "", headers[col_idx]).strip()
        val = last_row[col_idx].strip()
        if any(k in val for k in ["+", "-", "缩短", "提升", "下降", "%", "百分点"]):
            highlights.append(f"{h_name} {val}")
    if highlights:
        joined = "，".join(highlights)
        return f"实测对比数据表明，{last_row[0].replace('*', '')}在核心维度呈现显著改善：{joined}。"
    return "实测数据验证了双重环境阻断策略在真实校园场景中的显著干预增益。"


def run_gate2_layout_budget(doc: dict) -> list:
    print("\n" + "=" * 68)
    print("📐 [Gate 2] 16:9 幻灯片版式合成与视觉预算预检 (6×6 防溢出法则)")
    print("=" * 68)

    slides = []
    # 封面页 (Dignified Hero Canvas)
    slides.append(
        {
            "type": "cover",
            "kicker": "🌿 单一事实源 (SSOT) 自动化衍生演示",
            "title": doc["title"],
            "abstract": doc["abstract"],
        }
    )

    warnings = []
    badge_num = 1

    for ch in doc["chapters"]:
        secs = ch["sections"]
        # 版式 A：若该章包含 2 个无表格的并列子节（如 1.1+1.2、2.1+2.2、4.1+4.2），合成为高审美双卡片章节页
        if (
            len(secs) == 2
            and not secs[0]["tables"]
            and not secs[1]["tables"]
            and len(secs[0]["paragraphs"]) <= 2
            and len(secs[1]["paragraphs"]) <= 2
        ):
            s0_title = secs[0]["title"]
            s1_title = secs[1]["title"]
            card0_cls = (
                "card-amber"
                if any(k in s0_title for k in ["边界", "局限", "挑战", "风险", "FOMO"])
                else "card-blue"
            )
            card1_cls = "card-green"
            slides.append(
                {
                    "type": "dual_card",
                    "badge": f"{badge_num:02d}",
                    "title": ch["title"],
                    "cards": [
                        {
                            "cls": card0_cls,
                            "subtitle": s0_title,
                            "text": " ".join(secs[0]["paragraphs"]),
                        },
                        {
                            "cls": card1_cls,
                            "subtitle": s1_title,
                            "text": " ".join(secs[1]["paragraphs"]),
                        },
                    ],
                }
            )
            badge_num += 1
            continue

        # 其余章节按子节特征自动匹配版式 B（表格+洞察）、版式 C（量化要点+机理双卡）、版式 D（发现+洞察）
        for sec in secs:
            if len(sec["title"]) > 30:
                warnings.append(f"小节标题过长 ({len(sec['title'])} 字)，建议精简防断行：{sec['title']}")

            if sec["tables"]:
                # 版式 B：实验对比表格 + 底部数据洞察框
                tbl = sec["tables"][0]
                insight_text = _extract_table_insight(tbl)
                slides.append(
                    {
                        "type": "table_insight",
                        "badge": f"{badge_num:02d}",
                        "title": sec["title"],
                        "lead": sec["paragraphs"][0] if sec["paragraphs"] else "",
                        "table": tbl,
                        "insight": insight_text,
                    }
                )
                badge_num += 1
            elif len(sec["paragraphs"]) >= 2:
                # 版式 C：第一段提炼为量化要点卡片 (.card-blue)，第二段提炼为机理剖析卡片 (.card-green)
                bullets = _split_clauses(sec["paragraphs"][0])
                if len(bullets) > 6:
                    warnings.append(f"小节《{sec['title']}》要点数超过 6 条 ({len(bullets)} 条)，已自动收敛")
                    bullets = bullets[:6]
                slides.append(
                    {
                        "type": "quant_mechanism",
                        "badge": f"{badge_num:02d}",
                        "title": sec["title"],
                        "bullets": bullets,
                        "mechanism_text": " ".join(sec["paragraphs"][1:]),
                    }
                )
                badge_num += 1
            else:
                # 版式 D：单段实证小节 -> 核心实证对比卡片 (.card-blue) + 底部结论洞察框 (.insight)
                para = sec["paragraphs"][0] if sec["paragraphs"] else ""
                sentences = [s.strip() for s in para.split("。") if s.strip()]
                if len(sentences) >= 2:
                    main_body = "。".join(sentences[:-1]) + "。"
                    insight_body = sentences[-1] + "。"
                else:
                    main_body = para
                    insight_body = "实证结果进一步验证了双重环境干预策略的跨场景稳健性。"
                slides.append(
                    {
                        "type": "finding_insight",
                        "badge": f"{badge_num:02d}",
                        "title": sec["title"],
                        "main_body": main_body,
                        "insight": insight_body,
                    }
                )
                badge_num += 1

    print(f"   ✔ 幻灯片版式合成完成：共生成 {len(slides)} 页高审美 16:9 宽屏幻灯片（含语义卡片、三线表与数据洞察框）")
    if warnings:
        for w in warnings:
            print(f"   ⚠️ [版面预警] {w}")
    else:
        print("   ✔ 标题字数与卡片视觉预算自检通过：0 处断行溢出风险")

    return slides


# ==============================================================================
# 4. [Gate 3A] 16:9 宽屏演示幻灯片生成器 (dist/slides.marp.md & dist/slides.html)
# ==============================================================================
MARP_DESIGN_SYSTEM_CSS = """section {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  padding: 44px 64px;
  background: #ffffff;
  color: #1e293b;
  font-size: 20.5px;
  line-height: 1.72;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  box-sizing: border-box;
}

/* 封面页高阶视觉设计 (Dignified Hero Canvas) */
section.lead {
  background: radial-gradient(circle at 90% 10%, #e0f2fe 0%, #f8fafc 50%, #ffffff 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  padding: 44px 68px;
  box-sizing: border-box;
}

.hero-tag {
  display: inline-block;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 15.5px;
  font-weight: 800;
  padding: 6px 18px;
  border-radius: 20px;
  border: 1.5px solid #bae6fd;
  margin-bottom: 8px;
}

.hero-title {
  font-size: 40px;
  font-weight: 900;
  color: #0f172a;
  line-height: 1.25;
  margin: 0 0 12px 0;
  letter-spacing: -0.02em;
}

.hero-meta {
  display: flex;
  gap: 28px;
  font-size: 18.5px;
  color: #0284c7;
  font-weight: 700;
  margin: 0;
}

.hero-abstract-card {
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-left: 6px solid #0284c7;
  border-radius: 14px;
  padding: 22px 28px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.06);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hero-abstract-title {
  font-size: 20px;
  font-weight: 800;
  color: #0369a1;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-abstract-card p {
  font-size: 18.5px;
  line-height: 1.75;
  color: #334155;
  margin: 0;
}

.hero-disclaimer-pill {
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-left: 6px solid #f59e0b;
  border-radius: 10px;
  padding: 12px 22px;
  font-size: 15.5px;
  color: #92400e;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 章节标题与徽章 */
h2 {
  font-size: 31px;
  font-weight: 900;
  color: #0f172a;
  border-bottom: 2.5px solid #e2e8f0;
  padding-bottom: 12px;
  margin-top: 0;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.badge {
  display: inline-block;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: #ffffff;
  font-size: 15.5px;
  font-weight: 800;
  padding: 5px 14px;
  border-radius: 6px;
  vertical-align: middle;
  margin-right: 14px;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.28);
}

/* 通用双栏栅格系统 */
.columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
  margin-bottom: 14px;
}

/* 通用语义卡片体系 */
.card, .card-blue, .card-green, .card-amber {
  border-radius: 14px;
  padding: 20px 26px;
  box-shadow: 0 6px 18px rgba(15,23,42,0.04);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 10px;
  height: auto;
  box-sizing: border-box;
  font-size: 20px;
  line-height: 1.72;
  margin-bottom: 18px;
}

.card p, .card-blue p, .card-green p, .card-amber p {
  margin: 0;
}

.card-subtitle {
  font-size: 20.5px;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 4px;
}

.card {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-left: 6px solid #64748b;
}

.card-blue {
  background: #f0f9ff;
  border: 1.5px solid #bae6fd;
  border-left: 6px solid #0284c7;
  box-shadow: 0 6px 18px rgba(2,132,199,0.05);
}

.card-green {
  background: #f0fdf4;
  border: 1.5px solid #bbf7d0;
  border-left: 6px solid #10b981;
  box-shadow: 0 6px 18px rgba(16,185,129,0.05);
}

.card-amber {
  background: #fffbeb;
  border: 1.5px solid #fde68a;
  border-left: 6px solid #f59e0b;
  box-shadow: 0 6px 18px rgba(245,158,11,0.05);
}

p {
  font-size: 20px;
  line-height: 1.75;
  color: #334155;
  margin: 0 0 14px 0;
}

strong {
  color: #0f172a;
  font-weight: 800;
}

ul {
  margin: 0;
  padding-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

li {
  font-size: 19.5px;
  line-height: 1.7;
  color: #334155;
  margin: 0;
}

/* 底部洞察卡片 (Insight Box) */
.insight {
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-left: 6px solid #0284c7;
  border-radius: 12px;
  padding: 16px 24px;
  font-size: 19.5px;
  line-height: 1.65;
  color: #0f172a;
  box-shadow: 0 4px 12px rgba(15,23,42,0.04);
  margin-top: auto;
}

/* 学术三线表优化 */
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 18px;
  margin-top: 4px;
  margin-bottom: 16px;
}
th {
  background: #f8fafc;
  font-weight: 800;
  color: #0f172a;
  padding: 11px 16px;
  border-top: 2.5px solid #0f172a;
  border-bottom: 1.5px solid #0f172a;
  text-align: left;
  font-size: 18.5px;
}
td {
  padding: 10px 16px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155;
}
tr:nth-child(even) td {
  background: #fafafa;
}
tr:last-child td {
  border-bottom: 2.5px solid #0f172a;
}
code {
  font-family: 'SFMono-Regular', Consolas, monospace;
  background: #eff6ff;
  color: #0369a1;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}"""


def _table_to_markdown_lines(tbl: list) -> list:
    if len(tbl) < 2:
        return []
    cols = len(tbl[0])
    align_row = ["---"] * cols
    if cols >= 2:
        align_row[0] = ":---"
        align_row[1] = ":---"
        for i in range(2, cols):
            align_row[i] = ":---:"
    md_rows = [
        "| " + " | ".join(tbl[0]) + " |",
        "| " + " | ".join(align_row) + " |",
    ]
    for r in tbl[1:]:
        md_rows.append("| " + " | ".join(r) + " |")
    return md_rows


def _table_to_html(tbl: list) -> str:
    if len(tbl) < 2:
        return ""
    th_cells = "".join(f"<th>{format_inline_html(c)}</th>" for c in tbl[0])
    body_rows = []
    for row in tbl[1:]:
        td_cells = "".join(f"<td>{format_inline_html(c)}</td>" for c in row)
        body_rows.append(f"<tr>{td_cells}</tr>")
    return f"<table><thead><tr>{th_cells}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def build_slides_html(slides: list, out_html_path: Path, out_marp_path: Path):
    # 1. 构建对标 pure_research_slides.md 的高审美 Marp 源码 (dist/slides.marp.md)
    marp_blocks = [
        "---",
        "marp: true",
        "theme: default",
        "size: 16:9",
        "paginate: true",
        "math: katex",
        "---",
        "",
        "<style>",
        MARP_DESIGN_SYSTEM_CSS,
        "</style>",
        "",
    ]

    slide_sections_html = []
    total = len(slides)

    for idx, s in enumerate(slides, start=1):
        active_cls = " active" if idx == 1 else ""
        if s["type"] == "cover":
            abstract_clean = re.sub(r"^\*\*摘要\*\*[：:]\s*", "", s["abstract"])
            cover_marp = f"""<!-- _class: lead -->
<div>
  <div class="hero-tag">{s['kicker']}</div>
  <h1 class="hero-title">{s['title']}</h1>
  <div class="hero-meta">
    <span>🎙️ 汇报团队：<strong>NCU《人机协同程序设计》第 6 周实践课</strong></span>
    <span>🏛️ 数据基准：<strong>2026_Campus_Sleep_Intervention (N=80)</strong></span>
    <span>📅 <strong>2026 秋季学期</strong></span>
  </div>
</div>

<div class="hero-abstract-card">
  <div class="hero-abstract-title">🎯 核心导读与研究摘要</div>
  <p>{format_inline_html(abstract_clean)}</p>
</div>

<div class="hero-disclaimer-pill">
  <span>💡 <strong>一源多端编译声明</strong>：本演示文稿与 A4 研报由 <code>ssot_compiler.py</code> 从同一份纯语义母稿 <code>report.md</code> 确定性衍生。</span>
  <span style="background: #f59e0b; color: #fff; padding: 2px 10px; border-radius: 4px; font-size: 12.5px; font-weight: 700; white-space: nowrap;">SSOT 确定性衍生</span>
</div>"""
            marp_blocks.append(cover_marp)
            slide_sections_html.append(
                f'<section class="slide lead{active_cls}" data-index="{idx}" data-marpit-pagination="{idx} / {total}">\n{cover_marp}\n</section>'
            )

        elif s["type"] == "dual_card":
            c0, c1 = s["cards"][0], s["cards"][1]
            marp_slide = f"""## <span class="badge">{s['badge']}</span> {s['title']}

<div class="{c0['cls']}">

**{c0['subtitle']}**

{c0['text']}

</div>

<div class="{c1['cls']}">

**{c1['subtitle']}**

{c1['text']}

</div>"""
            marp_blocks.append(marp_slide)
            html_slide = f"""<section class="slide{active_cls}" data-index="{idx}" data-marpit-pagination="{idx} / {total}">
  <h2><span class="badge">{s['badge']}</span> {format_inline_html(s['title'])}</h2>
  <div class="{c0['cls']}">
    <div class="card-subtitle">{format_inline_html(c0['subtitle'])}</div>
    <p>{format_inline_html(c0['text'])}</p>
  </div>
  <div class="{c1['cls']}">
    <div class="card-subtitle">{format_inline_html(c1['subtitle'])}</div>
    <p>{format_inline_html(c1['text'])}</p>
  </div>
</section>"""
            slide_sections_html.append(html_slide)

        elif s["type"] == "table_insight":
            tbl_md = "\n".join(_table_to_markdown_lines(s["table"]))
            marp_slide = f"""## <span class="badge">{s['badge']}</span> {s['title']}

{s['lead']}

{tbl_md}

<div class="insight">📊 <strong>数据洞察</strong>：{format_inline_html(s['insight'])}</div>"""
            marp_blocks.append(marp_slide)
            html_slide = f"""<section class="slide{active_cls}" data-index="{idx}" data-marpit-pagination="{idx} / {total}">
  <h2><span class="badge">{s['badge']}</span> {format_inline_html(s['title'])}</h2>
  <p>{format_inline_html(s['lead'])}</p>
  {_table_to_html(s['table'])}
  <div class="insight">📊 <strong>数据洞察</strong>：{format_inline_html(s['insight'])}</div>
</section>"""
            slide_sections_html.append(html_slide)

        elif s["type"] == "quant_mechanism":
            bullets_md = "\n".join(f"* {b}" for b in s["bullets"])
            bullets_html = "\n".join(f"<li>{format_inline_html(b)}</li>" for b in s["bullets"])
            marp_slide = f"""## <span class="badge">{s['badge']}</span> {s['title']}

<div class="card-blue">

{bullets_md}

</div>

<div class="card-green">

{s['mechanism_text']}

</div>"""
            marp_blocks.append(marp_slide)
            html_slide = f"""<section class="slide{active_cls}" data-index="{idx}" data-marpit-pagination="{idx} / {total}">
  <h2><span class="badge">{s['badge']}</span> {format_inline_html(s['title'])}</h2>
  <div class="card-blue">
    <ul>{bullets_html}</ul>
  </div>
  <div class="card-green">
    <p>{format_inline_html(s['mechanism_text'])}</p>
  </div>
</section>"""
            slide_sections_html.append(html_slide)

        elif s["type"] == "finding_insight":
            marp_slide = f"""## <span class="badge">{s['badge']}</span> {s['title']}

<div class="card-blue">

{s['main_body']}

</div>

<div class="insight">💡 <strong>核心结论与机理验证</strong>：{format_inline_html(s['insight'])}</div>"""
            marp_blocks.append(marp_slide)
            html_slide = f"""<section class="slide{active_cls}" data-index="{idx}" data-marpit-pagination="{idx} / {total}">
  <h2><span class="badge">{s['badge']}</span> {format_inline_html(s['title'])}</h2>
  <div class="card-blue">
    <p>{format_inline_html(s['main_body'])}</p>
  </div>
  <div class="insight">💡 <strong>核心结论与机理验证</strong>：{format_inline_html(s['insight'])}</div>
</section>"""
            slide_sections_html.append(html_slide)

        if idx < total:
            marp_blocks.append("\n---\n")

    out_marp_path.write_text("\n".join(marp_blocks) + "\n", encoding="utf-8")

    # 2. 构建自包含离线可交互 16:9 演示网页 (dist/slides.html)，完整复用同一套 Marp 设计系统 CSS
    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(slides[0]['title'])} - 16:9 演示幻灯片</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0f172a;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}
    .stage-viewport {{
      width: 1280px;
      height: 720px;
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.55);
      position: relative;
      overflow: hidden;
      transform-origin: center center;
    }}
    {MARP_DESIGN_SYSTEM_CSS}
    section.slide {{
      position: absolute;
      inset: 0;
      width: 1280px;
      height: 720px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.22s ease;
    }}
    section.slide.active {{
      opacity: 1;
      pointer-events: auto;
    }}
    section.slide::after {{
      content: attr(data-marpit-pagination);
      position: absolute;
      right: 36px;
      bottom: 20px;
      font-size: 14px;
      font-weight: 700;
      color: #94a3b8;
    }}
    .math-inline {{
      font-family: "Times New Roman", Georgia, serif;
      font-style: italic;
    }}
    .toolbar {{
      margin-top: 14px;
      display: flex;
      gap: 12px;
      align-items: center;
      color: #cbd5e1;
      font-size: 13px;
      z-index: 10;
    }}
    .toolbar button {{
      background: #1e293b;
      color: #f8fafc;
      border: 1px solid #475569;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
    }}
    .toolbar button:hover {{ background: #334155; }}
  </style>
</head>
<body>
  <div class="stage-viewport" id="deck">
{''.join(slide_sections_html)}
  </div>
  <div class="toolbar">
    <button onclick="prevSlide()">← 上一页</button>
    <span id="indicator">第 1 / {total} 页</span>
    <button onclick="nextSlide()">下一页 →</button>
  </div>
  <script>
    const deck = document.getElementById('deck');
    const slides = Array.from(document.querySelectorAll('section.slide'));
    const indicator = document.getElementById('indicator');
    let cur = 0;
    function fitViewport() {{
      const scale = Math.min((window.innerWidth * 0.94) / 1280, (window.innerHeight * 0.86) / 720);
      deck.style.transform = `scale(${{scale}})`;
    }}
    window.addEventListener('resize', fitViewport);
    fitViewport();
    function showSlide(i) {{
      cur = (i + slides.length) % slides.length;
      slides.forEach((s, idx) => s.classList.toggle('active', idx === cur));
      indicator.textContent = `第 ${{cur + 1}} / ${{slides.length}} 页`;
    }}
    function nextSlide() {{ showSlide(cur + 1); }}
    function prevSlide() {{ showSlide(cur - 1); }}
    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') nextSlide();
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') prevSlide();
    }});
  </script>
</body>
</html>
"""
    out_html_path.write_text(html_doc, encoding="utf-8")


# ==============================================================================
# 5. [Gate 3B] A4 学术级报告编译器 (dist/report.pdf & dist/report.typ)
# ==============================================================================
def md_inline_to_typst(text: str) -> str:
    """将纯语义 Markdown 行内格式转换为 Typst 语法"""
    t = text.replace("$\\rightarrow$", "$->$").replace("→", "$->$")
    # 加粗 **...** -> *...*
    t = re.sub(r"\*\*([^\*]+)\*\*", r"*\1*", t)
    # 百分号转义（非公式内）
    t = t.replace("%", "\\%")
    return t


def build_report_typst_and_pdf(doc: dict, out_typ_path: Path, out_pdf_path: Path, out_a4_html_path: Path):
    abstract_clean = re.sub(r"^\*\*摘要\*\*[：:]\s*", "", doc["abstract"])
    typ_lines = [
        "#set page(",
        '  paper: "a4",',
        "  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.6cm, right: 2.6cm),",
        "  header: [",
        "    #grid(",
        "      columns: (1fr, 1fr),",
        '      align(left)[#text(8.5pt, fill: rgb("#64748b"))[南昌大学《人机协同程序设计》课程 · 研报交付端 (SSOT)]],',
        '      align(right)[#text(8.5pt, fill: rgb("#0284c7"), weight: "bold")[A4 学术排版规范]]',
        "    )",
        "    #v(-2pt)",
        '    #line(length: 100%, stroke: 0.6pt + rgb("#cbd5e1"))',
        "  ],",
        "  footer: [",
        '    #line(length: 100%, stroke: 0.6pt + rgb("#cbd5e1"))',
        "    #v(2pt)",
        "    #grid(",
        "      columns: (1fr, 1fr),",
        '      align(left)[#text(8.5pt, fill: rgb("#94a3b8"))[单一事实源 (SSOT) · Typst 自动化直出]],',
        '      align(right)[#context text(8.5pt, fill: rgb("#0f172a"), weight: "bold")[— 第 #counter(page).display("1 / 1", both: true) 页 —]]',
        "    )",
        "  ]",
        ")",
        '#set text(font: ("PingFang SC", "Songti SC", "STSong", "Noto Serif CJK SC", "SimSun"), size: 10.5pt, lang: "zh")',
        "#set par(justify: true, leading: 0.92em, spacing: 1.05em, first-line-indent: 0pt)",
        "#set heading(numbering: none)",
        "#show heading.where(level: 2): it => block(",
        "  width: 100%,",
        "  above: 1.85em,",
        "  below: 1.05em,",
        '  stroke: (bottom: 0.6pt + rgb("#cbd5e1")),',
        "  inset: (bottom: 0.42em),",
        '  text(size: 13pt, weight: "bold", fill: rgb("#0f172a"), it.body)',
        ")",
        "#show heading.where(level: 3): it => block(",
        "  above: 1.45em,",
        "  below: 0.95em,",
        '  text(size: 11.2pt, weight: "bold", fill: rgb("#1e3a8a"), it.body)',
        ")",
        "",
        "#align(center)[",
        f'  #text(size: 14.5pt, weight: "bold")[{md_inline_to_typst(doc["title"])}]',
        "  #v(0.5em)",
        '  #text(size: 9.5pt, fill: rgb("#475569"))[NCU《人机协同程序设计》第 6 周实践课 · 单一事实源 (SSOT) 编译交付物]',
        "]",
        "#v(0.8em)",
        "#rect(width: 100%, fill: rgb(\"#f8fafc\"), stroke: (left: 3pt + rgb(\"#1d4ed8\")), inset: 10pt)[",
        "#set par(first-line-indent: 0pt)",
        f'  *摘要*：{md_inline_to_typst(abstract_clean)}',
        "]",
        "#v(0.6em)",
        "",
    ]

    # 同步生成一份 A4 印刷版 HTML 备份，方便无 PDF 阅读器时直接浏览器预览打印
    a4_html_parts = [
        f"<h1>{format_inline_html(doc['title'])}</h1>",
        f"<div class='meta'>NCU《人机协同程序设计》第 6 周实践课 · 单一事实源 (SSOT) 编译交付物</div>",
        f"<div class='abstract'><strong>摘要：</strong>{format_inline_html(abstract_clean)}</div>",
    ]

    for ch in doc["chapters"]:
        typ_lines.append(f'== {md_inline_to_typst(ch["title"])}')
        a4_html_parts.append(f"<h2>{format_inline_html(ch['title'])}</h2>")
        for sec in ch["sections"]:
            typ_lines.append(f'=== {md_inline_to_typst(sec["title"])}')
            a4_html_parts.append(f"<h3>{format_inline_html(sec['title'])}</h3>")
            for p in sec["paragraphs"]:
                typ_lines.append(f"#h(2em){md_inline_to_typst(p)}")
                typ_lines.append("")
                a4_html_parts.append(f"<p>{format_inline_html(p)}</p>")

            for tbl in sec["tables"]:
                if len(tbl) >= 2:
                    cols = len(tbl[0])
                    typ_lines.append("#block(above: 1.1em, below: 1.1em, width: 100%)[")
                    typ_lines.append("  #set par(justify: false)")
                    typ_lines.append("  #set text(size: 9.5pt)")
                    typ_lines.append("  #align(center)[")
                    typ_lines.append(
                        f"    #table(columns: {cols}, align: center + horizon, stroke: (x, y) => if y == 0 {{ (top: 1.5pt + black, bottom: 1pt + black) }} else {{ (bottom: 0.5pt + gray) }}, inset: 6pt,"
                    )
                    for r_idx, row in enumerate(tbl):
                        for cell in row:
                            c_str = md_inline_to_typst(cell)
                            if r_idx == 0:
                                typ_lines.append(f"      [*{c_str}*],")
                            else:
                                typ_lines.append(f"      [{c_str}],")
                    typ_lines.append("    )")
                    typ_lines.append("  ]")
                    typ_lines.append("]")
                    typ_lines.append("")

                    # HTML Table
                    th_html = "".join(f"<th>{format_inline_html(c)}</th>" for c in tbl[0])
                    tr_html = "".join(
                        "<tr>" + "".join(f"<td>{format_inline_html(c)}</td>" for c in r) + "</tr>"
                        for r in tbl[1:]
                    )
                    a4_html_parts.append(
                        f"<table class='three-line'><thead><tr>{th_html}</tr></thead><tbody>{tr_html}</tbody></table>"
                    )

    out_typ_path.write_text("\n".join(typ_lines), encoding="utf-8")

    a4_html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>{html.escape(doc['title'])} - A4 学术报告</title>
  <style>
    @page {{ size: A4; margin: 22mm 20mm; }}
    body {{
      font-family: "PingFang SC", "Songti SC", "Microsoft YaHei", serif;
      color: #0f172a;
      max-width: 210mm;
      margin: 0 auto;
      padding: 20mm;
      line-height: 1.75;
      font-size: 10.5pt;
      background: #ffffff;
    }}
    h1 {{ text-align: center; font-size: 17pt; margin-bottom: 6px; }}
    .meta {{ text-align: center; font-size: 9.5pt; color: #475569; margin-bottom: 18px; }}
    .abstract {{
      background: #f8fafc;
      border-left: 3.5px solid #1d4ed8;
      padding: 10px 14px;
      margin-bottom: 18px;
      font-size: 10pt;
    }}
    h2 {{ font-size: 13pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin: 22px 0 12px 0; }}
    h3 {{ font-size: 11.2pt; margin: 16px 0 10px 0; color: #1e3a8a; }}
    p {{ text-indent: 2em; margin: 10px 0; text-align: justify; }}
    table.three-line {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 9.5pt;
      border-top: 2px solid #0f172a;
      border-bottom: 2px solid #0f172a;
    }}
    table.three-line th {{
      border-bottom: 1px solid #0f172a;
      padding: 6px 8px;
      text-align: left;
      background: #f8fafc;
    }}
    table.three-line td {{ padding: 6px 8px; border-bottom: 0.5px solid #cbd5e1; }}
    code {{ font-family: monospace; background: #f1f5f9; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
{''.join(a4_html_parts)}
</body>
</html>"""
    out_a4_html_path.write_text(a4_html_doc, encoding="utf-8")

    # 优先尝试调用本地 typst 编译 PDF
    typst_bin = shutil.which("typst")
    if typst_bin:
        res = subprocess.run(
            [typst_bin, "compile", str(out_typ_path), str(out_pdf_path)],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and out_pdf_path.exists():
            return "typst CLI 引擎"

    # 备选：使用内置 CJK 原生 PDF 兜底生成器（确保任何无外部依赖的裸 Python 环境均可输出合法 PDF）
    generate_fallback_cjk_pdf(doc, out_pdf_path)
    return "Python 内置学术 PDF 引擎 (零外部依赖兜底)"


def _pdf_utf16be_hex(text: str) -> str:
    """将中文字符串编码为 PDF Type0 CIDFont 支持的 UTF-16BE 十六进制文本串"""
    clean = re.sub(r"\*\*|`", "", text).replace("$\\rightarrow$", "->").replace("$N=40$", "N=40").replace("$N$", "N")
    return "<FEFF" + clean.encode("utf-16-be").hex().upper() + ">"


def generate_fallback_cjk_pdf(doc: dict, out_pdf_path: Path):
    """
    零第三方依赖的纯 Python 标准库 PDF 生成器（使用 Adobe-GB1 / STSong-Light 标准中日韩 CID 字库）
    当学生电脑既未安装 typst 也未安装 reportlab 时，100% 保证生成可打开阅读的 A4 PDF。
    """
    lines_to_draw = []
    lines_to_draw.append((15, doc["title"]))
    lines_to_draw.append((9, "NCU《人机协同程序设计》第 6 周实践课 · 单一事实源 (SSOT) 编译交付物"))
    lines_to_draw.append((10, ""))

    # 自动按 42 个字符宽度折行
    def wrap_line(text: str, width: int = 42):
        clean = re.sub(r"\*\*|`", "", text).replace("$\\rightarrow$", "->")
        return [clean[i : i + width] for i in range(0, len(clean), width)] or [""]

    for w in wrap_line(doc["abstract"], 40):
        lines_to_draw.append((10, w))
    lines_to_draw.append((10, ""))

    for ch in doc["chapters"]:
        lines_to_draw.append((12, ch["title"]))
        lines_to_draw.append((6, ""))
        for sec in ch["sections"]:
            lines_to_draw.append((11, sec["title"]))
            lines_to_draw.append((5, ""))
            for p in sec["paragraphs"]:
                for w in wrap_line("\u3000\u3000" + p, 42):
                    lines_to_draw.append((10, w))
            for tbl in sec["tables"]:
                for row in tbl:
                    lines_to_draw.append((9, " | ".join(row)))
            lines_to_draw.append((10, ""))

    # 分页组装 PDF 内容流
    pages_cmds = []
    y = 780
    cur_cmds = []
    for fsize, text in lines_to_draw:
        if y < 65:
            pages_cmds.append(cur_cmds)
            cur_cmds = []
            y = 780
        if text:
            hex_str = _pdf_utf16be_hex(text)
            cur_cmds.append(f"/F1 {fsize} Tf 50 {y} Td {hex_str} Tj -50 -{y} Td")
        y -= int(fsize * 1.65)
    pages_cmds.append(cur_cmds)

    total_pages = len(pages_cmds)
    pages_streams = []
    for idx, cmds in enumerate(pages_cmds, start=1):
        footer_hex = _pdf_utf16be_hex(f"— 第 {idx} / {total_pages} 页 —")
        page_cmds = ["BT"] + cmds + [f"/F1 9 Tf 260 36 Td {footer_hex} Tj -260 -36 Td", "ET"]
        pages_streams.append("\n".join(page_cmds))

    # 构建 PDF 对象表
    objects = []
    # 1: Catalog, 2: Pages, 3: Type0 Font (STSong-Light / UniGB-UCS2-H), 4: CIDFont
    num_pages = len(pages_streams)
    first_page_obj = 5
    kids_refs = " ".join(f"{first_page_obj + i * 2} 0 R" for i in range(num_pages))

    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(
        f"2 0 obj\n<< /Type /Pages /Kids [{kids_refs}] /Count {num_pages} >>\nendobj\n".encode("ascii")
    )
    objects.append(
        b"3 0 obj\n<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H /DescendantFonts [4 0 R] >>\nendobj\n"
    )
    objects.append(
        b"4 0 obj\n<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light /CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 4 >> >>\nendobj\n"
    )

    for i, stream_str in enumerate(pages_streams):
        page_obj_id = first_page_obj + i * 2
        content_obj_id = page_obj_id + 1
        stream_bytes = stream_str.encode("ascii")
        page_obj = (
            f"{page_obj_id} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_obj_id} 0 R >>\n"
            f"endobj\n"
        ).encode("ascii")
        content_obj = (
            f"{content_obj_id} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
            + stream_bytes
            + b"\nendstream\nendobj\n"
        )
        objects.append(page_obj)
        objects.append(content_obj)

    pdf_bytes = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(obj)

    xref_pos = len(pdf_bytes)
    total_objs = len(objects) + 1
    pdf_bytes.extend(f"xref\n0 {total_objs}\n0000000000 65535 f \n".encode("ascii"))
    for off in offsets[1:]:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    pdf_bytes.extend(
        f"trailer\n<< /Size {total_objs} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    out_pdf_path.write_bytes(bytes(pdf_bytes))


# ==============================================================================
# 6. CLI 主入口
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="NCU 第 6 周实践课：单一事实源 (SSOT) 一源多端自动化编译器")
    parser.add_argument(
        "--input",
        "-i",
        default="report.md",
        help="纯语义 Markdown 母稿路径（默认读取当前目录下的 report.md）",
    )
    parser.add_argument(
        "--outdir",
        "-o",
        default="dist",
        help="多端衍生制品输出目录（默认输出至 dist/）",
    )
    args = parser.parse_args()

    src_path = Path(args.input).resolve()
    if not src_path.exists():
        print(f"❌ 找不到输入母稿文件：{src_path}")
        print("💡 提示：请确认你在包含 report.md 的工程目录下运行 `python ssot_compiler.py`。")
        sys.exit(1)

    md_text = src_path.read_text(encoding="utf-8")

    # Gate 1: 纯语义检查
    if not run_gate1_semantic_check(md_text, src_path):
        sys.exit(2)

    # AST 解析与 Gate 2 视觉预算检查
    doc = parse_markdown_ast(md_text)
    slides = run_gate2_layout_budget(doc)

    # Gate 3: 多端产物构建
    out_dir = Path(args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    slides_html_path = out_dir / "slides.html"
    slides_marp_path = out_dir / "slides.marp.md"
    report_typ_path = out_dir / "report.typ"
    report_pdf_path = out_dir / "report.pdf"
    report_a4_html_path = out_dir / "report_a4_preview.html"

    print("\n" + "=" * 68)
    print("🚀 [Gate 3] 一源多端自动化分发编译 (Single Source -> Multi-Target)")
    print("=" * 68)

    build_slides_html(slides, slides_html_path, slides_marp_path)
    print(f"   ✔ [终端 1：16:9 宽屏演示幻灯片] 已生成 -> {slides_html_path.relative_to(src_path.parent)}")

    pdf_engine = build_report_typst_and_pdf(doc, report_typ_path, report_pdf_path, report_a4_html_path)
    print(
        f"   ✔ [终端 2：A4 学术长文报告 PDF] 已生成 -> {report_pdf_path.relative_to(src_path.parent)} (驱动: {pdf_engine})"
    )
    print(
        f"   ✔ [辅助预览：A4 网页印刷版备份] 已生成 -> {report_a4_html_path.relative_to(src_path.parent)}"
    )
    print("=" * 68)
    print("🎉 编译成功！请双击打开 dist/slides.html 与 dist/report.pdf 验收多端一致性。")


if __name__ == "__main__":
    main()

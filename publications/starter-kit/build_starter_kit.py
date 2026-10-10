#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


PAGE_W, PAGE_H = A4
MARGIN_X = 20 * mm
TOP_Y = PAGE_H - 25 * mm
BOTTOM_Y = 19 * mm

INK = HexColor("#14213D")
TEAL = HexColor("#0F7C78")
ORANGE = HexColor("#F59E0B")
PALE = HexColor("#EAF3F2")
PALE_ORANGE = HexColor("#FFF4DB")
LIGHT = HexColor("#F4F6F8")
MID = HexColor("#667085")
RULE = HexColor("#D8DEE8")
WHITE = colors.white

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
pdfmetrics.registerFont(TTFont("E7Sans", FONT_REG))
pdfmetrics.registerFont(TTFont("E7Sans-Bold", FONT_BOLD))
pdfmetrics.registerFont(TTFont("E7Mono", FONT_MONO))


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def inline_markup(text: str) -> str:
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='E7Mono'>\1</font>", text)
    return text


def paragraph_style(
    name: str,
    size: float,
    leading: float,
    color=INK,
    font="E7Sans",
    space_after=3.5 * mm,
) -> ParagraphStyle:
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=TA_LEFT,
        spaceAfter=space_after,
        splitLongWords=False,
        allowWidows=0,
        allowOrphans=0,
    )


STYLES = {
    "h1": paragraph_style("h1", 22, 27, INK, "E7Sans-Bold", 6 * mm),
    "h2": paragraph_style("h2", 14, 18, TEAL, "E7Sans-Bold", 3.5 * mm),
    "h3": paragraph_style("h3", 10.5, 13.5, ORANGE, "E7Sans-Bold", 2.5 * mm),
    "body": paragraph_style("body", 9.3, 13.2, INK, "E7Sans", 3.0 * mm),
    "small": paragraph_style("small", 8.0, 10.5, MID, "E7Sans", 1.8 * mm),
    "bullet": paragraph_style("bullet", 9.0, 12.4, INK, "E7Sans", 2.0 * mm),
    "quote": paragraph_style("quote", 10.2, 14.2, INK, "E7Sans-Bold", 0),
    "table": paragraph_style("table", 7.8, 10.2, INK, "E7Sans", 0),
    "table_head": paragraph_style("table_head", 7.8, 10.2, WHITE, "E7Sans-Bold", 0),
}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    _, raw, body = text.split("---\n", 2)
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, body


def split_pages(body: str) -> list[str]:
    return [p.strip() for p in body.split("<!-- PAGE -->") if p.strip()]


class PageRenderer:
    def __init__(self, c: canvas.Canvas, page_no: int, total_pages: int):
        self.c = c
        self.page_no = page_no
        self.total_pages = total_pages
        self.y = TOP_Y
        self.content_w = PAGE_W - 2 * MARGIN_X

    def background(self):
        self.c.setFillColor(WHITE)
        self.c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        self.c.setFillColor(TEAL)
        self.c.rect(0, PAGE_H - 7 * mm, PAGE_W, 7 * mm, stroke=0, fill=1)
        self.c.setStrokeColor(RULE)
        self.c.setLineWidth(0.5)
        self.c.line(MARGIN_X, 15 * mm, PAGE_W - MARGIN_X, 15 * mm)
        self.c.setFillColor(MID)
        self.c.setFont("E7Sans", 7.2)
        self.c.drawString(MARGIN_X, 10.5 * mm, "E7G-T Practical Starter Kit")
        self.c.drawRightString(
            PAGE_W - MARGIN_X,
            10.5 * mm,
            f"{self.page_no} / {self.total_pages}",
        )

    def require(self, height: float):
        if self.y - height < BOTTOM_Y:
            raise RuntimeError(
                f"Page {self.page_no} overflow: needs {height/mm:.1f} mm at y={self.y/mm:.1f} mm"
            )

    def draw_paragraph(self, text: str, style_key: str = "body", indent=0, width=None):
        width = width or (self.content_w - indent)
        p = Paragraph(inline_markup(text), STYLES[style_key])
        _, h = p.wrap(width, PAGE_H)
        self.require(h + STYLES[style_key].spaceAfter)
        p.drawOn(self.c, MARGIN_X + indent, self.y - h)
        self.y -= h + STYLES[style_key].spaceAfter

    def draw_bullet(self, text: str, number: str | None = None):
        marker = number if number else "•"
        marker_w = 8 * mm
        p = Paragraph(inline_markup(text), STYLES["bullet"])
        _, h = p.wrap(self.content_w - marker_w, PAGE_H)
        self.require(h + 2 * mm)
        self.c.setFillColor(TEAL if number is None else ORANGE)
        self.c.setFont("E7Sans-Bold", 8.6)
        self.c.drawString(MARGIN_X + 1 * mm, self.y - 3.2 * mm, marker)
        p.drawOn(self.c, MARGIN_X + marker_w, self.y - h)
        self.y -= h + 2.0 * mm

    def draw_quote(self, text: str):
        p = Paragraph(inline_markup(text), STYLES["quote"])
        inner_w = self.content_w - 16 * mm
        _, h = p.wrap(inner_w, PAGE_H)
        box_h = h + 10 * mm
        self.require(box_h + 5 * mm)
        self.c.setFillColor(PALE)
        self.c.roundRect(MARGIN_X, self.y - box_h, self.content_w, box_h, 3 * mm, 0, 1)
        self.c.setFillColor(TEAL)
        self.c.roundRect(MARGIN_X, self.y - box_h, 4 * mm, box_h, 2 * mm, 0, 1)
        p.drawOn(self.c, MARGIN_X + 10 * mm, self.y - 5 * mm - h)
        self.y -= box_h + 5 * mm

    def draw_table(self, rows: list[list[str]]):
        clean = [[c.strip() for c in row] for row in rows]
        if len(clean) > 1 and all(re.fullmatch(r":?-{3,}:?", c) for c in clean[1]):
            clean.pop(1)
        cols = len(clean[0])
        widths = [self.content_w / cols] * cols
        if cols == 2:
            widths = [self.content_w * 0.36, self.content_w * 0.64]
        elif cols == 3:
            widths = [self.content_w * 0.36, self.content_w * 0.34, self.content_w * 0.30]
        elif cols == 4:
            widths = [self.content_w * 0.28, self.content_w * 0.30, self.content_w * 0.20, self.content_w * 0.22]
        pdata = []
        for r_idx, row in enumerate(clean):
            style = STYLES["table_head"] if r_idx == 0 else STYLES["table"]
            pdata.append([Paragraph(inline_markup(cell or " "), style) for cell in row])
        t = Table(pdata, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), INK),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
                    ("GRID", (0, 0), (-1, -1), 0.4, RULE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        _, h = t.wrap(self.content_w, PAGE_H)
        self.require(h + 5 * mm)
        t.drawOn(self.c, MARGIN_X, self.y - h)
        self.y -= h + 5 * mm

    def draw_fill_line(self, text: str):
        label, _, rest = text.partition(":")
        if not rest.strip().startswith("["):
            self.draw_paragraph(text)
            return
        self.draw_paragraph(f"**{label}:**", "body")
        box_h = 10 * mm
        self.require(box_h + 2 * mm)
        self.c.setFillColor(LIGHT)
        self.c.setStrokeColor(RULE)
        self.c.roundRect(MARGIN_X, self.y - box_h, self.content_w, box_h, 1.5 * mm, 1, 1)
        self.y -= box_h + 2.5 * mm


def render_cover(c: canvas.Canvas, meta: dict[str, str], total_pages: int):
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Geometry motif: source configurations, projection, and phase bands.
    c.setLineWidth(1.0)
    c.setStrokeColor(HexColor("#486284"))
    cx, cy = PAGE_W * 0.73, PAGE_H * 0.73
    radii = [18, 34, 51, 69]
    for i, r in enumerate(radii):
        c.circle(cx, cy, r * mm / 2.8, stroke=1, fill=0)
    c.setFillColor(TEAL)
    for dx, dy, size in [(-25, 16, 4), (3, 31, 3), (30, 8, 5), (-2, -18, 4)]:
        c.circle(cx + dx * mm, cy + dy * mm, size * mm / 2, stroke=0, fill=1)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(2.2)
    c.line(cx - 31 * mm, cy + 18 * mm, cx + 35 * mm, cy - 13 * mm)
    c.setFillColor(ORANGE)
    c.circle(cx + 35 * mm, cy - 13 * mm, 2.6 * mm, stroke=0, fill=1)

    c.setFillColor(TEAL)
    c.rect(0, 0, 15 * mm, PAGE_H, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(15 * mm, 0, 3.5 * mm, PAGE_H, stroke=0, fill=1)

    x = 31 * mm
    c.setFillColor(WHITE)
    c.setFont("E7Sans-Bold", 46)
    c.drawString(x, 176 * mm, "E7G-T")

    c.setFillColor(ORANGE)
    c.setFont("E7Sans-Bold", 19)
    c.drawString(x, 155 * mm, "PRACTICAL STARTER KIT")

    subtitle = Paragraph(
        inline_markup(meta.get("subtitle", "")),
        paragraph_style("cover_sub", 15, 21, WHITE, "E7Sans", 0),
    )
    subtitle.wrapOn(c, 130 * mm, 60 * mm)
    subtitle.drawOn(c, x, 112 * mm)

    c.setFillColor(HexColor("#C9D5E6"))
    c.setFont("E7Sans", 9.5)
    c.drawString(x, 79 * mm, "A concise guide, quick-check method,")
    c.drawString(x, 73 * mm, "worked example, and reusable worksheet")

    c.setStrokeColor(HexColor("#486284"))
    c.line(x, 59 * mm, PAGE_W - 25 * mm, 59 * mm)
    c.setFillColor(WHITE)
    c.setFont("E7Sans-Bold", 10.5)
    c.drawString(x, 48 * mm, meta.get("author", ""))
    c.setFont("E7Sans", 8.5)
    c.setFillColor(HexColor("#C9D5E6"))
    c.drawString(x, 41.5 * mm, meta.get("edition", ""))
    c.drawString(x, 35.5 * mm, f"Based on {meta.get('kernel', '')}")
    c.drawRightString(PAGE_W - 20 * mm, 17 * mm, f"1 / {total_pages}")


def render_content_page(c: canvas.Canvas, text: str, page_no: int, total_pages: int):
    r = PageRenderer(c, page_no, total_pages)
    r.background()
    lines = text.splitlines()
    i = 0
    paragraph_buf: list[str] = []

    def flush_paragraph():
        if paragraph_buf:
            joined = " ".join(s.strip() for s in paragraph_buf)
            if re.match(r"^\*\*[^*]+:\*\*\s*\[", joined):
                r.draw_fill_line(joined.replace("**", ""))
            else:
                r.draw_paragraph(joined)
            paragraph_buf.clear()

    while i < len(lines):
        raw = lines[i].rstrip()
        stripped = raw.strip()
        if not stripped:
            flush_paragraph()
            i += 1
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = [[c for c in line.strip("|").split("|")] for line in table_lines]
            r.draw_table(rows)
            continue

        flush_paragraph()
        if stripped.startswith("# "):
            r.draw_paragraph(stripped[2:], "h1")
        elif stripped.startswith("## "):
            r.draw_paragraph(stripped[3:], "h2")
        elif stripped.startswith("### "):
            r.draw_paragraph(stripped[4:], "h3")
        elif stripped.startswith("> "):
            r.draw_quote(stripped[2:])
        elif re.match(r"^\d+\.\s+", stripped):
            m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
            r.draw_bullet(m.group(2), number=m.group(1))
        elif stripped.startswith("- "):
            r.draw_bullet(stripped[2:])
        else:
            paragraph_buf.append(stripped)
        i += 1
    flush_paragraph()


def build(source: Path, output: Path):
    raw = source.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    pages = split_pages(body)
    total_pages = len(pages)
    if total_pages != 13:
        raise RuntimeError(f"Expected 13 pages, found {total_pages}")

    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=A4, pageCompression=1)
    c.setTitle(meta.get("title", "E7G-T Practical Starter Kit"))
    c.setAuthor(meta.get("author", "Oleksandr Razinkov"))
    c.setSubject("Practical introduction to the E7G-T geometry-thinking framework")
    c.setKeywords("E7G-T, geometry-thinking, representation, projection, operational phase, worksheet")

    render_cover(c, meta, total_pages)
    c.showPage()
    for idx, page in enumerate(pages[1:], start=2):
        render_content_page(c, page, idx, total_pages)
        c.showPage()
    c.save()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_starter_kit.py SOURCE.md OUTPUT.pdf")
    build(Path(sys.argv[1]), Path(sys.argv[2]))

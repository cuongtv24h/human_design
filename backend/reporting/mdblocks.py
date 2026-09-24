"""Tiny Markdown → block model shared by the PDF and DOCX renderers.

Covers exactly the dialect our renderers (template + LLM editor) produce:
headings, paragraphs (line breaks kept), bullet / numbered lists with nesting,
blockquotes, GFM tables, horizontal rules, fenced code, and inline
``**bold**``, ``*italic*``, ```code``` and ``[links](url)`` (rendered as text).
Raw HTML is treated as plain text — never interpreted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# --- inline -----------------------------------------------------------------


@dataclass(frozen=True)
class Span:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False


Inline = list[Span]

_INLINE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<link>\[(?P<ltext>[^\]]+)\]\((?P<url>[^)\s]+)\))"
    r"|(?P<bold>\*\*)"
    r"|(?P<italic>(?<![\w*])\*(?=[^\s*])|(?<=[^\s*])\*(?![\w*])|(?<![\w_])_(?=[^\s_])|(?<=[^\s_])_(?![\w_]))"
)


def parse_inline(text: str) -> Inline:
    """Split a line into styled spans. Unbalanced markers stay literal."""
    balanced_bold = text.count("**") % 2 == 0
    spans: Inline = []
    bold = italic = False
    pos = 0

    def emit(chunk: str, **extra: bool) -> None:
        if chunk:
            spans.append(Span(chunk, bold=extra.get("bold", bold), italic=extra.get("italic", italic),
                              code=extra.get("code", False)))

    for match in _INLINE.finditer(text):
        kind = match.lastgroup
        if kind == "bold" and not balanced_bold:
            continue
        emit(text[pos:match.start()])
        pos = match.end()
        if kind == "code":
            emit(match.group("code")[1:-1], code=True)
        elif kind == "link":
            emit(match.group("ltext"))
        elif kind == "bold":
            bold = not bold
        elif kind == "italic":
            italic = not italic
    emit(text[pos:])
    return _merge(spans)


def _merge(spans: Inline) -> Inline:
    merged: Inline = []
    for span in spans:
        if merged and (merged[-1].bold, merged[-1].italic, merged[-1].code) == (span.bold, span.italic, span.code):
            merged[-1] = Span(merged[-1].text + span.text, span.bold, span.italic, span.code)
        else:
            merged.append(span)
    return merged


def plain(inline: Inline) -> str:
    return "".join(span.text for span in inline)


# --- blocks -----------------------------------------------------------------


@dataclass
class Heading:
    level: int
    text: Inline


@dataclass
class Paragraph:
    lines: list[Inline]


@dataclass
class ListItem:
    level: int
    lines: list[Inline]
    number: int | None = None  # set for ordered items


@dataclass
class ListBlock:
    items: list[ListItem] = field(default_factory=list)


@dataclass
class Quote:
    lines: list[Inline]


@dataclass
class Table:
    header: list[Inline]
    rows: list[list[Inline]]


@dataclass
class Rule:
    pass


@dataclass
class Code:
    text: str


Block = Heading | Paragraph | ListBlock | Quote | Table | Rule | Code

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_LIST = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*+]|\d{1,3}[.)])\s+(?P<text>.*)$")
_RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def _cells(line: str) -> list[Inline]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [parse_inline(cell.strip()) for cell in body.split("|")]


def parse_blocks(markdown: str) -> list[Block]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    blocks: list[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            blocks.append(Code("\n".join(code)))
            i += 1
            continue
        heading = _HEADING.match(stripped)
        if heading:
            blocks.append(Heading(len(heading.group(1)), parse_inline(heading.group(2))))
            i += 1
            continue
        if _RULE.match(stripped):
            blocks.append(Rule())
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]):
            header = _cells(stripped)
            rows: list[list[Inline]] = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = _cells(lines[i])
                rows.append((row + [[]] * len(header))[: len(header)])
                i += 1
            blocks.append(Table(header, rows))
            continue
        if stripped.startswith(">"):
            quote: list[Inline] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(parse_inline(lines[i].strip()[1:].strip()))
                i += 1
            blocks.append(Quote([q for q in quote if q] or quote))
            continue
        if _LIST.match(line):
            block = ListBlock()
            while i < len(lines):
                current = lines[i]
                item = _LIST.match(current)
                if item:
                    indent = len(item.group("indent").expandtabs(4))
                    marker = item.group("marker")
                    number = int(marker[:-1]) if marker[0].isdigit() else None
                    block.items.append(ListItem(min(indent // 2, 3), [parse_inline(item.group("text"))], number))
                    i += 1
                elif current.strip() and current.startswith((" ", "\t")) and block.items:
                    block.items[-1].lines.append(parse_inline(current.strip()))
                    i += 1
                else:
                    break
            blocks.append(block)
            continue
        para: list[Inline] = []
        while i < len(lines):
            current = lines[i]
            s = current.strip()
            if (not s or _HEADING.match(s) or s.startswith((">", "```")) or _LIST.match(current)
                    or _RULE.match(s) or (s.startswith("|") and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]))):
                break
            para.append(parse_inline(s))
            i += 1
        blocks.append(Paragraph(para))
    return blocks


__all__ = [
    "Block", "Code", "Heading", "Inline", "ListBlock", "ListItem", "Paragraph", "Quote", "Rule", "Span",
    "Table", "parse_blocks", "parse_inline", "plain",
]

"""Khối nội dung tùy chỉnh cho mẫu báo cáo (Giai đoạn 1).

Một block là văn bản Markdown tĩnh kèm biến trong danh sách trắng::

    Xin chào {{subject.name}} — bạn thuộc loại **{{chart.type_vn}}**.
    {{#if chart.hanging_gates}}Các cổng treo của bạn: {{#each chart.hanging_gates}}{{this.gate}} {{/each}}{{/if}}

Hỗ trợ ``{{var}}``, ``{{#if var}}...{{/if}}`` và ``{{#each list}}...{{/each}}``
(với ``{{this}}`` / ``{{this.key}}``). Không thực thi code — chỉ tra cứu trong
context dựng sẵn từ chart đã tính + thông tin người nhận + biến tổ chức.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_TOOLS_DIR = str(Path(__file__).resolve().parents[2] / "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from hd_calculator import GATE_MEANINGS, GATE_TO_CENTER  # noqa: E402
from hd_time import display_birth  # noqa: E402

from .language_vn import (  # noqa: E402
    CENTER_VN,
    vn_authority,
    vn_center,
    vn_channel,
    vn_definition,
    vn_strategy,
    vn_type,
)

BLOCK_KINDS = ("intro", "core", "practice", "outro", "disclaimer")

# Loại khối (để nhóm trong UI) -> SectionKind của hợp đồng báo cáo.
BLOCK_KIND_TO_SECTION_KIND = {
    "intro": "summary",
    "core": "core",
    "practice": "practice",
    "outro": "appendix",
    "disclaimer": "appendix",
}

BLOCK_VARIABLES: tuple[dict[str, str], ...] = (
    {"path": "subject.name", "label": "Tên người nhận", "example": "Nguyễn Văn A"},
    {"path": "subject.birth_display", "label": "Ngày giờ sinh (hiển thị)", "example": "15/05/1990 08:30 (giờ Việt Nam)"},
    {"path": "subject.birth_date", "label": "Ngày sinh", "example": "1990-05-15"},
    {"path": "subject.birth_time", "label": "Giờ sinh", "example": "08:30"},
    {"path": "subject.birth_place", "label": "Nơi sinh", "example": "Hòa Bình"},
    {"path": "chart.type", "label": "Type (gốc)", "example": "Generator"},
    {"path": "chart.type_vn", "label": "Type (tiếng Việt)", "example": "Người kiến tạo"},
    {"path": "chart.strategy", "label": "Chiến lược (gốc)", "example": "To Respond"},
    {"path": "chart.strategy_vn", "label": "Chiến lược (tiếng Việt)", "example": "Chờ để đáp ứng"},
    {"path": "chart.authority", "label": "Thẩm quyền (gốc)", "example": "Sacral"},
    {"path": "chart.authority_vn", "label": "Thẩm quyền (tiếng Việt)", "example": "Quyền xương cùng"},
    {"path": "chart.profile", "label": "Profile", "example": "1/3"},
    {"path": "chart.definition", "label": "Định nghĩa (gốc)", "example": "Single Definition"},
    {"path": "chart.definition_vn", "label": "Định nghĩa (tiếng Việt)", "example": "Định nghĩa đơn"},
    {"path": "chart.incarnation_cross", "label": "Chữ thập hóa thân", "example": "Right Angle Cross of ..."},
    {"path": "chart.cross_type", "label": "Loại chữ thập", "example": "Right Angle"},
    {"path": "chart.defined_centers", "label": "Trung tâm định nghĩa (EN)", "example": "[Sacral, G, ...]"},
    {"path": "chart.defined_centers_vn", "label": "Trung tâm định nghĩa (VN)", "example": "[Xương cùng, G, ...]"},
    {"path": "chart.defined_centers_count", "label": "Số trung tâm định nghĩa", "example": "5"},
    {"path": "chart.open_centers_vn", "label": "Trung tâm mở (VN)", "example": "[Đầu, ...]"},
    {"path": "chart.defined_channels", "label": "Kênh định nghĩa", "example": "[1-8, 20-34]"},
    {"path": "chart.defined_channels_count", "label": "Số kênh định nghĩa", "example": "4"},
    {"path": "chart.hanging_gates", "label": "Cổng treo (danh sách số)", "example": "[12, 22]"},
    {"path": "chart.hanging_gates_count", "label": "Số cổng treo", "example": "6"},
    {"path": "chart.gates.personality_sun", "label": "Cổng Mặt Trời nhân cách", "example": "10"},
    {"path": "chart.gates.personality_earth", "label": "Cổng Trái Đất nhân cách", "example": "15"},
    {"path": "chart.gates.design_sun", "label": "Cổng Mặt Trời thiết kế", "example": "46"},
    {"path": "chart.gates.design_earth", "label": "Cổng Trái Đất thiết kế", "example": "25"},
    {"path": "org.<tên biến>", "label": "Biến tổ chức (VD: org.hotline)", "example": "1900 6868"},
)

_KNOWN_VAR_PREFIXES = ("subject.", "chart.", "org.")


def build_block_context(chart: dict[str, Any], subject: dict[str, Any],
                        org_vars: dict[str, str] | None = None) -> dict[str, Any]:
    """Dựng context tra cứu cho block từ chart đã tính (không giờ UTC nội bộ)."""
    chart_type = str(chart.get("type", ""))
    defined = [str(c) for c in chart.get("defined_centers", []) or []]
    defined_set = set(defined)
    channels = [f"{min(int(a), int(b))}-{max(int(a), int(b))}"
                for a, b in (chart.get("defined_channels", []) or [])]
    connected = {int(g) for ch in (chart.get("defined_channels", []) or []) for g in ch}
    activated = [int(g) for g in (chart.get("all_activated_gates", []) or [])]
    hanging = sorted(set(activated) - connected)
    return {
        "subject": {
            "name": subject.get("name", "") or "",
            "birth_date": subject.get("birth_date", "") or "",
            "birth_time": subject.get("birth_time", "") or "",
            "birth_place": subject.get("birth_place", "") or subject.get("birth_location", "") or "",
            "birth_display": display_birth(str(subject.get("birth_date", "") or ""),
                                           str(subject.get("birth_time", "") or ""),
                                           str(subject.get("timezone", "+07:00") or "+07:00")),
        },
        "chart": {
            "type": chart_type,
            "type_vn": vn_type(chart_type),
            "strategy": str(chart.get("strategy", "")),
            "strategy_vn": vn_strategy(str(chart.get("strategy", "")), chart_type),
            "authority": str(chart.get("authority", "")),
            "authority_vn": vn_authority(str(chart.get("authority", ""))),
            "profile": str(chart.get("profile", "")),
            "definition": str(chart.get("definition", "")),
            "definition_vn": vn_definition(str(chart.get("definition", ""))),
            "incarnation_cross": str(chart.get("incarnation_cross", "")),
            "cross_type": str(chart.get("cross_type", "")),
            "defined_centers": defined,
            "defined_centers_vn": [vn_center(c) for c in defined],
            "defined_centers_count": len(defined),
            "open_centers": [c for c in CENTER_VN if c not in defined_set],
            "open_centers_vn": [vn_center(c) for c in CENTER_VN if c not in defined_set],
            "centers": [{"name": c, "name_vn": vn_center(c),
                         "status": "defined" if c in defined_set else "open"} for c in CENTER_VN],
            "defined_channels": channels,
            "defined_channels_count": len(channels),
            "hanging_gates": hanging,
            "hanging_gates_count": len(hanging),
            "hanging_gates_detail": [{"gate": g, "center": GATE_TO_CENTER.get(g, ""),
                                      "center_vn": vn_center(GATE_TO_CENTER.get(g, "")),
                                      "meaning": GATE_MEANINGS.get(g, "")} for g in hanging],
            "gates": {
                "personality_sun": chart.get("p_sun_gate"),
                "personality_earth": chart.get("p_earth_gate"),
                "design_sun": chart.get("d_sun_gate"),
                "design_earth": chart.get("d_earth_gate"),
            },
        },
        "org": dict(org_vars or {}),
    }


_TOKEN_RE = re.compile(r"\{\{\s*(#if\b|#each\b|/if\b|/each\b)?\s*([^{}]*?)\s*\}\}")


def _resolve(path: str, context: dict[str, Any]) -> tuple[Any, bool]:
    node: Any = context
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None, False
    return node, True


def _parse(template: str) -> tuple[list, list[str]]:
    """Phân tích template thành cây node đơn giản; lỗi cú pháp thành warning."""
    root: list = []
    stack: list[tuple[str, list]] = [("root", root)]
    warnings: list[str] = []
    pos = 0
    for match in _TOKEN_RE.finditer(template):
        if match.start() > pos:
            stack[-1][1].append(("text", template[pos:match.start()]))
        directive, expr = match.group(1) or "", match.group(2).strip()
        if directive in ("#if", "#each"):
            node: list = []
            stack[-1][1].append((directive[1:], expr, node))
            stack.append((directive[1:], node))
        elif directive in ("/if", "/each"):
            want = directive[1:]
            if len(stack) > 1 and stack[-1][0] == want:
                stack.pop()
            else:
                warnings.append(f"Thẻ đóng {match.group(0)} không khớp.")
                stack[-1][1].append(("text", match.group(0)))
        else:
            stack[-1][1].append(("var", expr))
        pos = match.end()
    if pos < len(template):
        stack[-1][1].append(("text", template[pos:]))
    while len(stack) > 1:
        kind, _ = stack.pop()
        warnings.append(f"Thiếu thẻ đóng cho {{{{#{kind}}}}}.")
    return root, warnings


def _render_nodes(nodes: list, context: dict[str, Any], warnings: list[str]) -> str:
    out: list[str] = []
    for node in nodes:
        kind = node[0]
        if kind == "text":
            out.append(node[1])
        elif kind == "var":
            value, found = _resolve(node[1], context)
            if not found:
                warnings.append(f"Biến lạ {{{{{node[1]}}}}}: giữ trống.")
                continue
            if value is None:
                continue
            out.append(", ".join(str(v) for v in value) if isinstance(value, list) else str(value))
        elif kind == "if":
            value, found = _resolve(node[1], context)
            if not found:
                warnings.append(f"Biến lạ {{{{{node[1]}}}}}: coi như sai.")
            elif value:
                out.append(_render_nodes(node[2], context, warnings))
        elif kind == "each":
            value, found = _resolve(node[1], context)
            if not found or value is None:
                warnings.append(f"Biến lạ {{{{{node[1]}}}}}: bỏ qua vòng lặp.")
            elif not isinstance(value, list):
                warnings.append(f"Biến {{{{{node[1]}}}}} không phải danh sách: bỏ qua vòng lặp.")
            else:
                for item in value:
                    out.append(_render_nodes(node[2], {**context, "this": item}, warnings))
    return "".join(out)


def render_block(body: str, context: dict[str, Any]) -> tuple[str, list[str]]:
    """Render block -> (markdown, warnings). Không bao giờ raise với input lạ."""
    try:
        nodes, warnings = _parse(body or "")
        return _render_nodes(nodes, context, warnings), sorted(set(warnings))
    except Exception as exc:  # pragma: no cover - phòng thủ tuyệt đối
        return body or "", [f"Không render được khối: {exc}"]


def extract_variables(body: str) -> set[str]:
    """Liệt kê biến dùng trong block (để cảnh báo biến lạ ngay khi lưu)."""
    found = set()
    for match in _TOKEN_RE.finditer(body or ""):
        expr = (match.group(2) or "").strip()
        if not expr or expr == "this" or expr.startswith("this."):
            continue
        if any(expr == p[:-1] or expr.startswith(p) for p in _KNOWN_VAR_PREFIXES):
            found.add(expr.split()[0])
    return found


def channel_display(lo: int, hi: int) -> str:
    """Tên kênh song ngữ cho block cần (tái dùng language_vn)."""
    lang = vn_channel(lo, hi)
    return f"Kênh {lo}-{hi} · {lang['name']}" if lang else f"Kênh {lo}-{hi}"

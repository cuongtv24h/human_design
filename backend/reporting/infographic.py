"""Báo cáo tư vấn dạng Infographic HTML — trực quan, ít chữ, tập trung điểm chính.

Một file HTML tự chứa (CSS + BodyGraph SVG nội tuyến, không JS, không CDN):
mở offline được, gửi qua chat/email được, in ra A4 được.

Nguyên tắc nội dung (khớp ``docs/NARRATIVE_STANDARD.md``):
- Chỉ các điểm chính: Type · Strategy · Authority · Profile · Definition,
  9 trung tâm, la bàn quyết định 3 bước, tín hiệu đúng/lệch, việc làm ngay.
- Ít chữ: mỗi ô tối đa một câu ngắn, lấy từ lớp ngôn ngữ đời sống
  ``language_vn`` (không viết lại nội dung mới ở đây).
- Thuật ngữ song ngữ theo ``tools/hd_language.py``.
- Deterministic: dựng thẳng từ ``document.chart`` đã tính — không gọi LLM.
  Kênh & Chữ thập chỉ hiện ở gói ``deep_core``.
"""

from __future__ import annotations

import re
from html import escape
from typing import Any, Iterable

from .contract import ReportDocument, ReportTier
from .export import bodygraph_svg
from .language_vn import (
    AUTHORITY_LANGUAGE,
    CENTER_LANGUAGE,
    CENTER_ORDER,
    CROSS_TYPE_LANGUAGE,
    DEFINITION_LANGUAGE,
    NOT_SELF_SIGNATURE,
    PROFILE_STORIES,
    TYPE_LANGUAGE,
    TYPE_VN,
    _SIGNAL_BY_AUTHORITY,
    resolve_authority,
    vn_authority,
    vn_center,
    vn_channel,
    vn_definition,
    vn_strategy,
)

# Mỗi Type một màu nhận diện — dùng cho dải tiêu đề, ô nhấn, trung tâm có màu.
TYPE_ACCENT: dict[str, str] = {
    "Generator": "#D9722B",
    "Manifesting Generator": "#C9463D",
    "Projector": "#3565A8",
    "Manifestor": "#7446A8",
    "Reflector": "#2A8C80",
}
DEFAULT_ACCENT = "#3565A8"

_SENTENCE_END = re.compile(r"(?:(?<=[.!?…])|(?<=[.!?…][\'\"”’)]))\s+")


def short(text: Any, limit: int = 120) -> str:
    """First sentence of ``text``, trimmed at a word boundary to ``limit`` chars."""
    value = " ".join(str(text or "").split())
    if not value:
        return ""
    parts = _SENTENCE_END.split(value, maxsplit=2)
    first = parts[0]
    # A lone rhetorical question says nothing — keep its answer too.
    if first.endswith("?") and len(parts) > 1:
        first = f"{first} {parts[1]}"
    if len(first) <= limit:
        return first
    cut = first[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:—-– ")
    return f"{cut}…"


def _tail(text: str) -> str:
    """Part after the first em dash — drops a repeated headline word."""
    value = str(text or "")
    return value.split(" — ", 1)[1] if " — " in value else value


def _note(text: str, avoid: str, limit: int) -> str:
    """First sentence of ``text`` that does not merely repeat ``avoid``."""
    norm = lambda v: re.sub(r"[\W_]+", "", v.lower())  # noqa: E731
    for sentence in _SENTENCE_END.split(" ".join(str(text or "").split())):
        if sentence and norm(sentence) != norm(avoid):
            return short(sentence, limit)
    return ""


def _headline(text: str) -> str:
    """Part before an em dash — ``"Trạm phát minh — nơi..."`` → ``"Trạm phát minh"``."""
    return str(text or "").split(" — ", 1)[0].strip()


def _e(value: Any) -> str:
    return escape(str(value or ""), quote=True)


def _gate_meanings() -> dict[int, str]:
    try:
        from hd_calculator import GATE_MEANINGS  # noqa: PLC0415

        return GATE_MEANINGS
    except Exception:  # pragma: no cover - calculator always importable in repo
        return {}


def _gate_label(gate: Any) -> str:
    meaning = _gate_meanings().get(int(gate), "") if str(gate).isdigit() else ""
    vn = meaning.split(" - ", 1)[-1] if meaning else ""
    return short(vn, 48)


def _inline_svg(svg: str) -> str:
    svg = re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg)
    return re.sub(r"^\s*<!DOCTYPE[^>]*>\s*", "", svg)


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------


def _tile(label: str, value: str, note: str, icon: str) -> str:
    return (
        '<div class="tile">'
        f'<div class="tile-icon" aria-hidden="true">{icon}</div>'
        f'<div class="tile-label">{_e(label)}</div>'
        f'<div class="tile-value">{_e(value)}</div>'
        f'<div class="tile-note">{_e(note)}</div>'
        "</div>"
    )


def _section(title: str, body: str, icon: str, extra_class: str = "") -> str:
    return (
        f'<section class="card {extra_class}">'
        f'<h2><span class="h-icon" aria-hidden="true">{icon}</span>{_e(title)}</h2>'
        f"{body}</section>"
    )


def _centers_block(defined: set[str]) -> str:
    count = len(defined)
    meter = "".join(
        f'<span class="dot {"on" if name in defined else ""}"></span>' for name in CENTER_ORDER
    )
    rows = []
    for name in CENTER_ORDER:
        lang = CENTER_LANGUAGE.get(name, {})
        is_on = name in defined
        state = "Có màu · ổn định" if is_on else "Mở · nhạy cảm"
        hint = _headline(lang.get("life_name", "")) if is_on else short(lang.get("open_question", ""), 90)
        rows.append(
            f'<li class="center {"on" if is_on else "open"}">'
            f'<div class="c-name">{_e(vn_center(name))}<span class="c-state">{state}</span></div>'
            f'<div class="c-hint">{_e(hint)}</div></li>'
        )
    return (
        f'<div class="meter"><div class="meter-dots">{meter}</div>'
        f'<div class="meter-text"><b>{count}/9</b> trung tâm có màu — nguồn lực ổn định của bạn. '
        f"<b>{9 - count}</b> trung tâm mở — nơi bạn dễ “hút” năng lượng người khác.</div></div>"
        f'<ul class="centers">{"".join(rows)}</ul>'
    )


def _steps_block(steps: Iterable[str]) -> str:
    items = "".join(
        f'<li class="step"><span class="step-no">{index}</span><span>{_e(short(step, 110))}</span></li>'
        for index, step in enumerate(steps, 1)
    )
    return f'<ol class="steps">{items}</ol>'


def _signal_block(chart_type: str, type_lang: dict[str, str]) -> str:
    not_self, signature = NOT_SELF_SIGNATURE.get(chart_type, ("", ""))
    return (
        '<div class="signals">'
        f'<div class="signal good"><div class="sig-label">Đang đi đúng (Signature)</div>'
        f'<div class="sig-word">{_e(signature)}</div>'
        f'<div class="sig-note">{_e(short(_tail(type_lang.get("signature_life", "")), 100))}</div></div>'
        '<div class="signal-arrow" aria-hidden="true">⇄</div>'
        f'<div class="signal bad"><div class="sig-label">Đang lệch nhịp (Not-Self)</div>'
        f'<div class="sig-word">{_e(not_self)}</div>'
        f'<div class="sig-note">{_e(short(_tail(type_lang.get("not_self_life", "")), 100))}</div></div>'
        "</div>"
    )


def _profile_block(profile: str, definition: str) -> str:
    story = PROFILE_STORIES.get(profile, {})
    definition_text = DEFINITION_LANGUAGE.get(definition, "")
    return (
        f'<div class="profile-name"><span class="pill">{_e(profile)}</span>'
        f'{_e(story.get("story_name", ""))}</div>'
        '<div class="split">'
        f'<div class="half"><div class="half-label">Bên trong (ý thức)</div>'
        f'<p>{_e(short(story.get("inner_life", ""), 120))}</p></div>'
        f'<div class="half"><div class="half-label">Bên ngoài (người khác thấy)</div>'
        f'<p>{_e(short(story.get("outer_life", ""), 120))}</p></div>'
        "</div>"
        f'<div class="definition"><b>{_e(vn_definition(definition))}:</b> '
        f"{_e(short(_tail(definition_text), 150))}</div>"
    )


def _channels_block(channels: Iterable[Any]) -> str:
    chips = []
    for pair in channels:
        a, b = sorted(int(g) for g in pair)
        lang = vn_channel(a, b) or {}
        chips.append(
            f'<li class="chip"><span class="chip-key">{a}-{b}</span>'
            f'<span class="chip-name">{_e(lang.get("name", ""))}</span>'
            f'<span class="chip-life">{_e(short(lang.get("life", ""), 100))}</span></li>'
        )
    if not chips:
        return '<p class="muted">Không có kênh định hình — bạn cảm nhận thế giới qua môi trường.</p>'
    return f'<ul class="chips">{"".join(chips)}</ul>'


def _cross_block(chart: dict[str, Any]) -> str:
    gates = [
        ("☉ Mặt Trời · Ý thức", chart.get("p_sun_gate")),
        ("⊕ Trái Đất · Ý thức", chart.get("p_earth_gate")),
        ("☉ Mặt Trời · Thiết kế", chart.get("d_sun_gate")),
        ("⊕ Trái Đất · Thiết kế", chart.get("d_earth_gate")),
    ]
    tiles = "".join(
        f'<div class="gate"><div class="gate-pos">{_e(pos)}</div>'
        f'<div class="gate-no">Cổng {_e(gate)}</div><div class="gate-mean">{_e(_gate_label(gate))}</div></div>'
        for pos, gate in gates
        if gate
    )
    framing = short(CROSS_TYPE_LANGUAGE.get(str(chart.get("cross_type", "")), ""), 130)
    return (
        f'<div class="cross-name">{_e(chart.get("incarnation_cross", ""))}</div>'
        f'<p class="muted">{_e(framing)}</p><div class="gates">{tiles}</div>'
    )


def _actions_block(type_lang: dict[str, str], authority: dict[str, Any], open_centers: list[str]) -> str:
    first_open = CENTER_LANGUAGE.get(open_centers[0], {}) if open_centers else {}
    actions = [
        ("Giữ năng lượng", short(type_lang.get("energy_protection", ""), 130)),
        ("Ra quyết định", short(authority.get("scenario_business", ""), 170)),
        (
            "Săn bọt biển",
            f"Mỗi tối hỏi mình một câu: “{short(first_open.get('open_question', ''), 90)}”"
            if first_open
            else "Mỗi tối ghi 1 dòng: hôm nay mình đã sống đúng nhịp ở đâu?",
        ),
    ]
    cards = "".join(
        f'<div class="action"><div class="action-no">{index}</div>'
        f'<div class="action-title">{_e(title)}</div><p>{_e(text)}</p></div>'
        for index, (title, text) in enumerate(actions, 1)
    )
    return f'<div class="actions">{cards}</div>'


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------


def render_infographic_html(document: ReportDocument, include_bodygraph: bool = True) -> str:
    """Render the one-page consulting infographic for ``document``."""
    chart = document.chart
    subject = document.subject
    chart_type = str(chart.get("type", ""))
    type_lang = TYPE_LANGUAGE.get(chart_type, {})
    authority_raw = str(chart.get("authority", ""))
    authority = AUTHORITY_LANGUAGE.get(resolve_authority(authority_raw), {})
    profile = str(chart.get("profile", ""))
    definition = str(chart.get("definition", ""))
    defined = set(chart.get("defined_centers", []))
    open_centers = [name for name in CENTER_ORDER if name not in defined]
    accent = TYPE_ACCENT.get(chart_type, DEFAULT_ACCENT)
    strategy = vn_strategy(str(chart.get("strategy", "")), chart_type)
    deep = document.tier is ReportTier.DEEP_CORE

    birth_bits = [f"{subject.birth_date} · {subject.birth_time} (UTC{subject.timezone})"]
    if subject.birth_location:
        birth_bits.append(subject.birth_location)

    one_liner = (
        f"Bạn là {type_lang.get('life_name', TYPE_VN.get(chart_type, chart_type)).lower()}: "
        f"{strategy.lower()}, và quyết định bằng {authority.get('compass_name', vn_authority(authority_raw)).lower()}."
    )

    tiles = "".join(
        [
            _tile("Loại năng lượng · Type", f"{chart_type} · {TYPE_VN.get(chart_type, '')}",
                  f"{type_lang.get('life_name', '')} — {type_lang.get('population', '')}", "◎"),
            _tile("Chiến lược · Strategy", strategy, _note(type_lang.get("strategy_life", ""), strategy, 110), "➜"),
            _tile("Quyền nội tại · Authority", vn_authority(authority_raw),
                  f"Tín hiệu đúng: {_SIGNAL_BY_AUTHORITY.get(resolve_authority(authority_raw), '')}", "✦"),
            _tile("Nhân cách · Profile", profile,
                  PROFILE_STORIES.get(profile, {}).get("story_name", ""), "◐"),
        ]
    )

    left_col = ""
    if include_bodygraph:
        left_col = (
            '<section class="card bodygraph"><h2><span class="h-icon" aria-hidden="true">✧</span>'
            "Bản đồ BodyGraph</h2>"
            f'<div class="svg-wrap">{_inline_svg(bodygraph_svg(document))}</div></section>'
        )

    sections = [
        f'<div class="grid-2">{left_col}'
        + _section("9 trung tâm năng lượng (9 Centers)", _centers_block(defined), "◉")
        + "</div>",
        '<div class="grid-2">'
        + _section(
            f"La bàn quyết định — {authority.get('compass_name', '')}",
            _steps_block(authority.get("steps", [])),
            "✦",
        )
        + _section("Tín hiệu cơ thể: đúng hay lệch?", _signal_block(chart_type, type_lang), "♡")
        + "</div>",
        _section("Nhân cách & Định nghĩa (Profile · Definition)", _profile_block(profile, definition), "◐"),
    ]
    if deep:
        sections.append(
            '<div class="grid-2">'
            + _section("Tài năng bẩm sinh — Kênh (Channels)", _channels_block(chart.get("defined_channels", [])), "⟷")
            + _section("Chủ đề cuộc đời — Chữ thập hóa thân (Incarnation Cross)", _cross_block(chart), "✚")
            + "</div>"
        )
    sections.append(_section("3 việc làm ngay tuần này", _actions_block(type_lang, authority, open_centers), "★", "highlight"))

    generated = document.provenance.generated_at.strftime("%d/%m/%Y")
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Infographic Human Design — {_e(subject.name or "Báo cáo")}</title>
<style>{_css(accent)}</style>
</head>
<body>
<main class="page">
<header class="hero">
  <div class="hero-text">
    <div class="eyebrow">Infographic tư vấn Human Design</div>
    <h1>{_e(subject.name or "Người được phân tích")}</h1>
    <div class="birth">{_e(" · ".join(birth_bits))}</div>
    <p class="one-liner">{_e(one_liner)}</p>
  </div>
  <div class="badge">
    <div class="badge-type">{_e(chart_type)}</div>
    <div class="badge-vn">{_e(type_lang.get("life_name", TYPE_VN.get(chart_type, "")))}</div>
    <div class="badge-pop">{_e(type_lang.get("population", ""))}</div>
  </div>
</header>
<div class="tiles">{tiles}</div>
{"".join(sections)}
<footer>
  Dữ liệu tính bằng Swiss Ephemeris · Tạo ngày {generated} · Human Design là công cụ tự quan sát,
  không thay thế tư vấn y tế, tâm lý hay tài chính chuyên môn. Hãy thử nghiệm và để trải nghiệm của chính bạn kiểm chứng.
</footer>
</main>
</body>
</html>
"""


def _css(accent: str) -> str:
    return f"""
:root {{ --accent: {accent}; --ink: #232227; --muted: #6B675E; --paper: #FBF8F1;
  --card: #FFFFFF; --line: #E8E2D4; --good: #2E8B57; --bad: #C0392B; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--paper); color: var(--ink);
  font: 15px/1.5 "Be Vietnam Pro", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
.page {{ max-width: 1120px; margin: 0 auto; padding: 28px 20px 40px; }}
.hero {{ display: flex; gap: 24px; align-items: center; justify-content: space-between;
  padding: 28px 32px; border-radius: 22px; color: #fff;
  background: linear-gradient(135deg, var(--accent), color-mix(in srgb, var(--accent) 55%, #111)); }}
.eyebrow {{ text-transform: uppercase; letter-spacing: .14em; font-size: 12px; opacity: .85; }}
h1 {{ margin: 6px 0 4px; font-size: 34px; line-height: 1.15; }}
.birth {{ opacity: .9; font-size: 14px; }}
.one-liner {{ margin: 14px 0 0; font-size: 18px; font-weight: 600; max-width: 640px; }}
.badge {{ flex: 0 0 auto; width: 190px; height: 190px; border-radius: 50%; display: flex;
  flex-direction: column; align-items: center; justify-content: center; text-align: center;
  background: rgba(255,255,255,.14); border: 2px solid rgba(255,255,255,.55); padding: 16px; }}
.badge-type {{ font-size: 13px; letter-spacing: .08em; text-transform: uppercase; opacity: .9; }}
.badge-vn {{ font-size: 20px; font-weight: 700; margin: 6px 0; line-height: 1.2; }}
.badge-pop {{ font-size: 12px; opacity: .85; }}
.tiles {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 18px 0; }}
.tile {{ background: var(--card); border: 1px solid var(--line); border-top: 5px solid var(--accent);
  border-radius: 16px; padding: 14px 16px; }}
.tile-icon {{ font-size: 20px; color: var(--accent); }}
.tile-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }}
.tile-value {{ font-size: 18px; font-weight: 700; margin: 4px 0 6px; line-height: 1.25; }}
.tile-note {{ font-size: 13px; color: var(--muted); }}
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 18px 20px;
  margin-bottom: 18px; break-inside: avoid; }}
.grid-2 > .card {{ margin-bottom: 0; }}
.card h2 {{ margin: 0 0 12px; font-size: 17px; display: flex; gap: 10px; align-items: center; }}
.h-icon {{ width: 30px; height: 30px; border-radius: 50%; display: inline-flex; align-items: center;
  justify-content: center; background: color-mix(in srgb, var(--accent) 14%, #fff); color: var(--accent); flex: 0 0 auto; }}
.svg-wrap svg {{ width: 100%; height: auto; display: block; border-radius: 12px; }}
.meter {{ display: flex; gap: 14px; align-items: center; margin-bottom: 12px; }}
.meter-dots {{ display: flex; gap: 5px; flex: 0 0 auto; }}
.dot {{ width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--accent); }}
.dot.on {{ background: var(--accent); }}
.meter-text {{ font-size: 13px; color: var(--muted); }}
.centers {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }}
.center {{ border-radius: 12px; padding: 8px 12px; border: 1.5px solid var(--accent); }}
.center.on {{ background: color-mix(in srgb, var(--accent) 12%, #fff); }}
.center.open {{ border-style: dashed; border-color: #C9C2B1; }}
.c-name {{ font-weight: 700; font-size: 14px; display: flex; justify-content: space-between; gap: 8px; }}
.c-state {{ font-weight: 500; font-size: 12px; color: var(--muted); white-space: nowrap; }}
.c-hint {{ font-size: 13px; color: var(--muted); }}
.steps {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }}
.step {{ display: flex; gap: 12px; align-items: flex-start; }}
.step-no {{ flex: 0 0 auto; width: 30px; height: 30px; border-radius: 50%; background: var(--accent);
  color: #fff; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; }}
.signals {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: stretch; }}
.signal {{ border-radius: 14px; padding: 12px 14px; }}
.signal.good {{ background: #EAF6EF; border: 1.5px solid var(--good); }}
.signal.bad {{ background: #FBECEA; border: 1.5px solid var(--bad); }}
.sig-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
.sig-word {{ font-size: 18px; font-weight: 700; margin: 4px 0; }}
.signal.good .sig-word {{ color: var(--good); }}
.signal.bad .sig-word {{ color: var(--bad); }}
.sig-note {{ font-size: 13px; color: var(--muted); }}
.signal-arrow {{ align-self: center; font-size: 22px; color: var(--muted); }}
.profile-name {{ font-size: 17px; font-weight: 700; display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }}
.pill {{ background: var(--accent); color: #fff; border-radius: 999px; padding: 2px 12px; font-size: 15px; }}
.split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.half {{ background: #F6F2E8; border-radius: 12px; padding: 10px 14px; }}
.half p {{ margin: 4px 0 0; }}
.half-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }}
.definition {{ margin-top: 12px; font-size: 14px; }}
.chips {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }}
.chip {{ display: grid; grid-template-columns: auto 1fr; column-gap: 10px; border-left: 4px solid var(--accent);
  background: #F9F7F1; border-radius: 10px; padding: 8px 12px; }}
.chip-key {{ grid-row: span 2; font-weight: 800; color: var(--accent); align-self: center; }}
.chip-name {{ font-weight: 700; font-size: 14px; }}
.chip-life {{ font-size: 13px; color: var(--muted); }}
.cross-name {{ font-weight: 700; font-size: 16px; }}
.gates {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }}
.gate {{ border: 1px solid var(--line); border-radius: 12px; padding: 8px 12px; }}
.gate-pos {{ font-size: 12px; color: var(--muted); }}
.gate-no {{ font-weight: 800; color: var(--accent); }}
.gate-mean {{ font-size: 13px; }}
.highlight {{ border: 2px solid var(--accent); background: color-mix(in srgb, var(--accent) 5%, #fff); }}
.actions {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
.action {{ background: #fff; border-radius: 14px; padding: 14px; border: 1px solid var(--line); }}
.action p {{ margin: 6px 0 0; font-size: 14px; }}
.action-no {{ width: 28px; height: 28px; border-radius: 8px; background: var(--accent); color: #fff;
  font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }}
.action-title {{ font-weight: 700; margin-top: 8px; }}
.muted {{ color: var(--muted); font-size: 13px; margin: 6px 0; }}
footer {{ margin-top: 10px; font-size: 12px; color: var(--muted); text-align: center; }}
@media (max-width: 860px) {{
  .hero {{ flex-direction: column; align-items: flex-start; }}
  .badge {{ width: 150px; height: 150px; }}
  .tiles {{ grid-template-columns: 1fr 1fr; }}
  .grid-2, .split, .actions {{ grid-template-columns: 1fr; }}
}}
@media print {{
  @page {{ size: A4; margin: 10mm; }}
  body {{ background: #fff; font-size: 12px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .page {{ padding: 0; max-width: none; }}
  .card, .tile, .hero {{ break-inside: avoid; }}
}}
"""


__all__ = ["TYPE_ACCENT", "render_infographic_html", "short"]

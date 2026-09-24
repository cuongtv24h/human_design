"""Chuẩn nội dung báo cáo tự sự: "Bản Thiết Kế Bản Thân — Cẩm Nang Vận Hành".

Bốn nhóm chủ đề cốt lõi và năm phần chuẩn được mô tả trong
``docs/NARRATIVE_STANDARD.md``. Renderer ở đây chỉ dùng (1) chart đã tính bởi
``tools/hd_calculator.py`` và (2) lớp ngôn ngữ ``language_vn`` — không LLM,
không đoán số, deterministic 100%.

Quy tắc vàng (xem NARRATIVE_STANDARD.md):
- Ngôn ngữ đời sống dẫn trước; thuật ngữ kỹ thuật chỉ ở dòng "Thuật ngữ:".
- Trục tâm lý của mỗi phần: thấu cảm → chỉ ra cơ chế → hành động cụ thể.
- 70% hành vi thực tế / 30% khái niệm kỹ thuật.
"""

from __future__ import annotations

from typing import Any

from .catalog import NARRATIVE_SECTIONS
from .language_vn import (
    AUTHORITY_LANGUAGE,
    CENTER_LANGUAGE,
    CENTER_ORDER,
    CROSS_FRAMING,
    CROSS_TYPE_LANGUAGE,
    DEFINITION_FALLBACK,
    DEFINITION_LANGUAGE,
    PROFILE_STORIES,
    TYPE_LANGUAGE,
    resolve_authority,
    seven_day_log,
)

PART_IDS: tuple[str, ...] = tuple(spec.id for spec in NARRATIVE_SECTIONS)


def _type_info(chart: dict[str, Any]) -> dict[str, str]:
    info = TYPE_LANGUAGE.get(chart.get("type", ""))
    if info is None:  # defensive: unknown type should never happen
        return TYPE_LANGUAGE["Generator"]
    return info


def _part1_identity(chart: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    t = _type_info(chart)
    lines = [
        f"{name or 'Bạn'} thân mến,",
        "",
        "Trước tiên, hãy hình dung một điều đơn giản: bạn sinh ra kèm theo một **bản thiết kế phần cứng** — "
        "giống như chiếc xe mà bạn không chọn, nhưng nó quyết định bạn chạy êm trên loại đường nào. "
        "Ép chiếc xe thể thao chạy đường rừng sẽ làm nó kiệt sức, dù tài xế có giỏi đến đâu. "
        "Biểu đồ BodyGraph chính là **bản vẽ kỹ thuật của chiếc xe đó**: 9 trạm năng lượng, "
        "những ống dẫn cố định và một chế độ vận hành mặc định.",
        "",
        f"**Chiếc xe của bạn là:** {t['car']}",
        "",
        "### Hào quang & vị trí tự nhiên của bạn",
        f"Bạn thuộc nhóm **{t['life_name']}** — {t['population']}. {t['aura']}",
        "",
        "### Tín hiệu đèn xanh – đèn đỏ",
        f"- **Đèn xanh — lúc nào bạn biết mình đi đúng đường:** {t['signature_life']}",
        f"- **Đèn đỏ — dấu hiệu bạn đang chạy sai nhiên liệu:** {t['not_self_life']}",
        "",
        "> *Thử ngay:* trong 7 ngày tới, mỗi tối chỉ cần hỏi một câu — *hôm nay đèn nào sáng nhiều hơn?*",
        "",
        f"_Thuật ngữ: Type = {chart.get('type', '')}._",
    ]
    return "\n".join(lines), {
        "type": chart.get("type"),
        "life_name": t["life_name"],
        "population": t["population"],
    }


def _part2_decision_compass(chart: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    t = _type_info(chart)
    authority_raw = chart.get("authority", "")
    a = AUTHORITY_LANGUAGE[resolve_authority(authority_raw)]
    steps = a["steps"]
    lines = [
        "Phần lớn sự hối hận không đến từ việc bạn chọn sai, mà từ việc bạn **dùng nhầm cơ quan để quyết định**. "
        "Phân tích bằng não cho bạn lý do; còn người thật sự đưa bạn đi đến cuối con đường là một 'cơ quan' khác. "
        f"Của bạn là: **{a['compass_name']}**.",
        "",
        "### Chiến lược tiếp cận cơ hội",
        f"**{t['strategy_life']}**",
        "",
        f"### La bàn của bạn: {a['compass_name']}",
        f"**Nguyên tắc vàng:** {a['rule']}",
        "",
        "**Ba bước để 'nghe' la bàn:**",
        f"1. {steps[0]}",
        f"2. {steps[1]}",
        f"3. {steps[2]}",
        "",
        "**Dùng ngay trong hai tình huống quen thuộc:**",
        f"- *Trước lời mời hợp tác:* {a['scenario_business']}",
        f"- *Trước quyết định mua sắm hoặc mối quan hệ:* {a['scenario_purchase']}",
        "",
        f"_Thuật ngữ: Strategy = {chart.get('strategy', '').split(' - ')[0]} · Authority = {authority_raw}._",
    ]
    return "\n".join(lines), {
        "strategy": chart.get("strategy"),
        "authority": authority_raw,
        "authority_key": resolve_authority(authority_raw),
        "compass_name": a["compass_name"],
    }


def _part3_burden_release(chart: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    defined = [c for c in CENTER_ORDER if c in set(chart.get("defined_centers", []))]
    open_centers = [c for c in CENTER_ORDER if c not in set(chart.get("defined_centers", []))]

    lines = [
        "Cơ thể bạn có **9 trạm năng lượng**. Những trạm đã 'có màu' (defined) là nhà máy điện riêng của bạn — "
        "chúng chạy ổn định mỗi ngày. Những trạm còn trống (open) là **chiếc bọt biển**: chúng không hỏng, "
        "chúng *mở cửa* — bạn hấp thu năng lượng từ người khác và từ môi trường, rồi đôi khi tưởng đó là chuyện của mình.",
        "",
        f"### Điểm tựa vững chắc — {len(defined)} trạm có màu",
    ]
    for center in defined:
        c = CENTER_LANGUAGE[center]
        lines.append(f"- **{c['life_name']}** — {c['defined_life']}")
    if defined:
        lines += [
            "",
            f"Đây là những gì bạn có thể tin 100% mỗi ngày, không sợ cạn: "
            + ", ".join(f"*{CENTER_LANGUAGE[c]['life_name'].split(' — ')[0]}*" for c in defined)
            + ".",
        ]

    lines += ["", f"### 'Những chiếc bọt biển' trong bạn — {len(open_centers)} trạm mở"]
    for center in open_centers:
        c = CENTER_LANGUAGE[center]
        lines += [
            f"- **{c['life_name']}** — {c['open_life']} "
            f"*Câu hỏi để nhận diện: {c['open_question']}*",
        ]
    if open_centers:
        lines += [
            "",
            "Mục đích không phải 'tắc' những trạm này — mà là học cách nhận diện: "
            "*cảm xúc này — của mình, hay của ai?*",
        ]

    lines += [
        "",
        f"_Thuật ngữ: Defined Centers = {', '.join(defined) or 'không có'} · "
        f"Open Centers = {', '.join(open_centers) or 'không có'}._",
    ]
    return "\n".join(lines), {
        "defined_centers": defined,
        "open_centers": open_centers,
    }


def _part4_role_profile(chart: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    profile = chart.get("profile", "")
    story = PROFILE_STORIES.get(profile)
    definition = chart.get("definition", "")
    definition_life = DEFINITION_LANGUAGE.get(definition, DEFINITION_FALLBACK)
    cross_type = chart.get("cross_type", "")
    cross_life = CROSS_TYPE_LANGUAGE.get(cross_type, cross_type)
    quarters = chart.get("quarters", {}) or {}

    lines = [
        "Profile là 'vai diễn' bạn nhận vào lúc sinh — một kịch bản gồm hai lớp: người **bên trong** "
        "(cách bạn thật sự xử lý đời) và hình ảnh **bên ngoài** (người ta nhìn thấy bạn thế nào).",
        "",
    ]
    if story:
        lines += [f"### Vai diễn của bạn: {profile} — \"{story['story_name']}\""]
        lines += [f"- *Người bên trong:* {story['inner_life']}", f"- *Hình ảnh bên ngoài:* {story['outer_life']}"]
        lines += ["", "### Bài học từ những lần vấp", story["mistake_reframe"]]
    else:
        lines += [f"### Vai diễn của bạn: {profile}", "(Chưa có kịch bản tự sự cho profile này trong lớp ngôn ngữ.)"]

    lines += [
        "",
        "### Cách bạn 'đóng gói' năng lượng",
        definition_life,
        "",
        "### Chủ đề lớn của cuộc đời (Incarnation Cross)",
        f"**{chart.get('incarnation_cross', '')}** — {cross_life.rstrip('.')}.",
        "",
        CROSS_FRAMING,
    ]
    if quarters:
        lines += [
            "",
            "Quarters: Personality Sun — "
            f"{quarters.get('p_sun', '')} · Personality Earth — {quarters.get('p_earth', '')} · "
            f"Design Sun — {quarters.get('d_sun', '')} · Design Earth — {quarters.get('d_earth', '')}.",
        ]
    lines += [
        "",
        f"_Thuật ngữ: Profile = {profile} · Definition = {definition} · "
        f"Cross gates = {chart.get('p_sun_gate')}/{chart.get('p_earth_gate')} "
        f"(Personality) · {chart.get('d_sun_gate')}/{chart.get('d_earth_gate')} (Design)._",
    ]
    return "\n".join(lines), {
        "profile": profile,
        "story_name": story["story_name"] if story else None,
        "definition": definition,
        "cross_type": cross_type,
        "incarnation_cross": chart.get("incarnation_cross"),
    }


def _part5_field_application(chart: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    t = _type_info(chart)
    open_center_count = len([c for c in CENTER_ORDER if c not in set(chart.get("defined_centers", []))])
    exercises = seven_day_log(chart.get("authority", ""), open_center_count)
    lines = [
        "Thiết kế chỉ trở thành 'vận hành' khi nó bước vào ba mặt phẳng của đời sống hằng ngày:",
        "",
        "### Trong công việc",
        t["work_fit"],
        f"**Bảo vệ năng lượng:** {t['energy_protection']}",
        "",
        "### Trong tình yêu & giao tiếp",
        t["relationship_hint"],
        "",
        "### Nhật ký thử nghiệm 7 ngày — chỉ 3 việc nhỏ",
        f"1. **{exercises[0]}**",
        f"2. **{exercises[1]}**",
        f"3. **{exercises[2]}**",
        "",
        "> Bạn không cần nhớ hết những gì đã đọc. Chọn **đúng một việc** trong ba việc trên, làm trong 7 ngày, "
        "và ghi lại 3 dòng mỗi tối. Thiết kế sẽ tự chứng minh cho bạn — bằng cảm giác, không bằng lý thuyết.",
        "",
        "_Lưu ý: Human Design là công cụ tự quan sát, không thay thế tư vấn y tế, pháp lý hay tài chính. "
        "Giờ sinh càng chính xác, bản vẽ càng sát với chiếc xe thật của bạn._",
    ]
    return "\n".join(lines), {
        "type": chart.get("type"),
        "open_center_count": open_center_count,
        "exercise_count": len(exercises),
    }


_RENDERERS = {
    NARRATIVE_SECTIONS[0].id: _part1_identity,
    NARRATIVE_SECTIONS[1].id: _part2_decision_compass,
    NARRATIVE_SECTIONS[2].id: _part3_burden_release,
    NARRATIVE_SECTIONS[3].id: _part4_role_profile,
    NARRATIVE_SECTIONS[4].id: _part5_field_application,
}


def render_operating_manual(chart: dict[str, Any], name: str = "") -> list[dict[str, Any]]:
    """Render the 5 standard narrative parts from a calculated chart.

    Returns one dict per part: id, title, kind, markdown, data, source_tools,
    knowledge_refs — ready to be wrapped into ``ReportSection`` objects by the
    orchestrator.
    """
    parts: list[dict[str, Any]] = []
    for spec in NARRATIVE_SECTIONS:
        markdown, data = _RENDERERS[spec.id](chart, name)
        parts.append(
            {
                "id": spec.id,
                "title": spec.title,
                "kind": spec.kind,
                "markdown": markdown,
                "data": data,
                "source_tools": list(spec.source_tools),
                "knowledge_refs": list(spec.knowledge_refs),
            }
        )
    return parts

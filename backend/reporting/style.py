"""Hồ sơ văn phong mẫu báo cáo (P2: B làm chính + A-lite hỗ trợ).

- Phân tích: LLM đọc bài mẫu -> JSON phẳng (tone/rhythm/vocabulary/structure/do/dont/excerpt).
- Tiêm: khối "## 8. Văn phong của mẫu" ghép vào brief LLM khi sinh báo cáo (kèm 1 đoạn trích minh họa).
"""

from __future__ import annotations

from typing import Mapping

ANALYSIS_SYSTEM = (
    "Bạn là chuyên gia phân tích văn phong tiếng Việt. Chỉ trả về MỘT object JSON hợp lệ, "
    "không thêm lời dẫn ngoài JSON."
)

_MAX_FIELD = 600
_MAX_ITEMS = 6


def build_style_analysis_brief(template_name: str, samples: list[tuple[str, str]], max_chars: int = 6000) -> str:
    """Prompt yêu cầu LLM trích hồ sơ văn phong (JSON phẳng, mọi value đều là string)."""
    chunks = [
        f'Phân tích văn phong của {len(samples)} bài mẫu dưới đây (mẫu báo cáo "{template_name}").',
        "Trả về JSON phẳng DUY NHẤT với đúng các key string sau (nội dung tiếng Việt):",
        '- "tone": giọng điệu tổng thể (1-2 câu).',
        '- "rhythm": nhịp câu, độ dài câu, cách ngắt đoạn (1-2 câu).',
        '- "vocabulary": cách dùng từ, mức độ thuật ngữ, ẩn dụ (1-2 câu).',
        '- "structure": cấu trúc đoạn/bài quen thuộc (1-2 câu).',
        '- "do": 3-6 điều NÊN làm khi viết theo giọng này, mỗi điều một dòng.',
        '- "dont": 3-6 điều cần TRÁNH, mỗi điều một dòng.',
        '- "excerpt": trích NGUYÊN VĂN 2-3 câu hay nhất, đặc trưng nhất từ bài mẫu (40-600 ký tự).',
        "Chỉ mô tả CÁCH VIẾT, không tóm tắt nội dung bài mẫu.",
    ]
    budget = max_chars
    for i, (title, body) in enumerate(samples, 1):
        text = (body or "").strip()
        if len(text) > budget:
            text = text[:budget].rsplit(" ", 1)[0] + "…"
        budget -= len(text)
        chunks.append(f"\n--- Bài mẫu {i}: {title} ---\n{text}")
        if budget <= 500:
            break
    return "\n".join(chunks)


def parse_style_profile(drafts: Mapping[str, str], sample_count: int) -> dict:
    """Chuẩn hóa JSON LLM trả về thành hồ sơ văn phong. Raise ValueError khi thiếu lõi."""
    def clean(key: str, limit: int = _MAX_FIELD) -> str:
        return str(drafts.get(key, "") or "").strip()[:limit]

    def items(key: str) -> list[str]:
        out = []
        for line in str(drafts.get(key, "") or "").splitlines():
            line = line.strip().lstrip("-•*0123456789. ").strip()
            if line:
                out.append(line[:200])
        return out[:_MAX_ITEMS]

    tone, excerpt = clean("tone"), clean("excerpt", 800)
    if not tone or len(excerpt) < 20:
        raise ValueError("AI chưa trích được văn phong (thiếu tone/excerpt).")
    return {
        "tone": tone,
        "rhythm": clean("rhythm"),
        "vocabulary": clean("vocabulary"),
        "structure": clean("structure"),
        "do": items("do"),
        "dont": items("dont"),
        "excerpt": excerpt,
        "sample_count": sample_count,
    }


def style_brief_block(snapshot: Mapping | None) -> str:
    """Khối "## 8" tiêm vào brief LLM (B: hồ sơ + A-lite: đoạn trích). Rỗng khi không có gì dùng được."""
    profile = ((snapshot or {}).get("profile") or {}) if isinstance(snapshot, Mapping) else {}
    if not isinstance(profile, Mapping):
        return ""
    name = (snapshot or {}).get("template_name", "") if isinstance(snapshot, Mapping) else ""
    tone = str(profile.get("tone", "") or "").strip()
    excerpt = str(profile.get("excerpt", "") or "").strip()
    if not tone and not excerpt:
        return ""
    lines = [f"## 8. Văn phong của mẫu{f' “{name}”' if name else ''} (bắt buộc tuân thủ)",
             "Viết theo đúng văn phong dưới đây. Đây là yêu cầu về CÁCH VIẾT — mọi dữ kiện kỹ thuật "
             "vẫn lấy từ dữ liệu nguồn, không bịa."]
    for label, key in (("Giọng điệu", "tone"), ("Nhịp câu", "rhythm"),
                       ("Từ vựng", "vocabulary"), ("Cấu trúc", "structure")):
        value = str(profile.get(key, "") or "").strip()
        if value:
            lines.append(f"- {label}: {value}")
    do_items = [str(x).strip() for x in (profile.get("do") or []) if str(x).strip()][:6]
    dont_items = [str(x).strip() for x in (profile.get("dont") or []) if str(x).strip()][:6]
    if do_items:
        lines.append("- Nên: " + "; ".join(do_items))
    if dont_items:
        lines.append("- Tránh: " + "; ".join(dont_items))
    if excerpt:
        lines.append("Ví dụ TRÍCH NGUYÊN VĂN từ bài mẫu — chỉ học cách viết, KHÔNG dùng lại nội dung/sự kiện trong đó:")
        lines.append(f'"{excerpt}"')
    return "\n".join(lines)

PREVIEW_SYSTEM = (
    "Bạn là biên tập viên tiếng Việt. Chỉ trả về MỘT object JSON hợp lệ, "
    "không thêm lời dẫn ngoài JSON."
)

DEFAULT_PREVIEW_TOPIC = (
    "Giới thiệu ngắn về Trung tâm Cổ Họng (Throat Center) trong Human Design cho người mới."
)


def build_style_preview_brief(topic: str, profile: Mapping, *, styled: bool) -> str:
    """Prompt viết thử 1 đoạn văn: giọng trung lập (A) hoặc theo hồ sơ văn phong (B)."""
    head = [
        "Viết một đoạn văn khoảng 120-180 từ về chủ đề dưới đây.",
        'Trả về JSON phẳng DUY NHẤT với đúng một key string: "preview" (toàn bộ đoạn văn).',
    ]
    if styled:
        head.append("TUÂN THỦ đúng văn phong mô tả dưới đây (CÁCH VIẾT, không bịa sự kiện):")
        for label, key in (("Giọng điệu", "tone"), ("Nhịp câu", "rhythm"),
                           ("Từ vựng", "vocabulary"), ("Cấu trúc", "structure")):
            value = str(profile.get(key, "") or "").strip()
            if value:
                head.append(f"- {label}: {value}")
        do_items = [str(x).strip() for x in (profile.get("do") or []) if str(x).strip()][:6]
        dont_items = [str(x).strip() for x in (profile.get("dont") or []) if str(x).strip()][:6]
        if do_items:
            head.append("- Nên: " + "; ".join(do_items))
        if dont_items:
            head.append("- Tránh: " + "; ".join(dont_items))
    else:
        head.append("Dùng giọng văn TRUNG LẬP, rõ ràng — không bắt chước văn phong đặc biệt nào.")
    head.append(f'Chủ đề: "{topic}"')
    return "\n".join(head)


def parse_style_preview(drafts: Mapping[str, str]) -> str:
    """Lấy đoạn văn từ JSON LLM trả về. Raise ValueError khi rỗng."""
    text = str(drafts.get("preview", "") or "").strip()
    if len(text) < 20:
        raise ValueError("AI chưa viết được đoạn thử.")
    return text[:2000]
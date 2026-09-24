#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hd_language.py — Chuẩn hoá ngôn từ tiếng Việt cho Human Design
================================================================
Mục đích: mọi nơi hiển thị (BodyGraph, báo cáo PDF, MCP/REST) đều dùng
cùng một bộ thuật ngữ tiếng Việt đã trau chuốt, KHÔNG dịch thô kiểu
"Chờ Đáp Ứng rồi Thông Báo".

Tên các trung tâm lấy theo ``knowledge/02_9_trung_tam.md`` (bản chuẩn của repo),
ví dụ "Đám rối Thái Dương", "Lá Lách", "Xương Cùng".

Dùng:
    from hd_language import vn_strategy, vn_authority, vn_definition, vn_type
    vn_strategy("Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo")
    # -> "Chờ phản hồi rồi thông báo"
"""

# --------------------------------------------------------------------------
# 1. CHIẾN LƯỢC (Strategy)
# --------------------------------------------------------------------------
STRATEGY_VN = {
    "Manifestor": "Thông báo trước khi hành động",
    "Generator": "Chờ đáp ứng rồi hành động",
    "Manifesting Generator": "Chờ phản hồi rồi thông báo",
    "Projector": "Chờ lời mời",
    "Reflector": "Chờ trọn một chu kỳ Mặt Trăng (28–29 ngày)",
}
STRATEGY_EN = {
    "Manifestor": "Inform before acting",
    "Generator": "Wait to respond",
    "Manifesting Generator": "Wait to respond, then inform",
    "Projector": "Wait for the invitation",
    "Reflector": "Wait a lunar cycle",
}

# --------------------------------------------------------------------------
# 2. QUYỀN NỘI TẠI (Authority)
# --------------------------------------------------------------------------
AUTHORITY_VN = {
    "Emotional - Solar Plexus": "Quyền Cảm xúc — Đám rối Thái Dương",
    "Emotional": "Quyền Cảm xúc — Đám rối Thái Dương",
    "Sacral": "Quyền Xương Cùng (Sacral)",
    "Splenic": "Quyền Lách (Splenic)",
    "Splenic - Splenic": "Quyền Lách (Splenic)",
    "Ego (Heart) - Manifested": "Quyền Bản ngã — Tim (biểu hiện ra ngoài)",
    "Ego (Heart)": "Quyền Bản ngã — Tim",
    "Ego - Manifested": "Quyền Bản ngã — Tim (biểu hiện ra ngoài)",
    "Ego": "Quyền Bản ngã — Tim",
    "Self-Projected (G-Center)": "Quyền Tự chiếu — Trung tâm G",
    "Self-Projected": "Quyền Tự chiếu — Trung tâm G",
    "Mental - Environment / No Inner Authority": "Dựa vào môi trường — không có quyền nội tại",
    "Mental - Environment": "Dựa vào môi trường — không có quyền nội tại",
    "Lunar - Reflector": "Quyền Mặt Trăng (Reflector)",
    "Lunar": "Quyền Mặt Trăng (Reflector)",
}

# --------------------------------------------------------------------------
# 3. ĐỊNH NGHĨA (Definition)
# --------------------------------------------------------------------------
DEFINITION_VN = {
    "No Definition": "Không định nghĩa",
    "Single Definition": "Định nghĩa đơn (một khối liền)",
    "Split Definition": "Định nghĩa chia tách (hai khối)",
    "Triple Split Definition": "Định nghĩa chia ba",
    "Quadruple Split Definition": "Định nghĩa chia bốn",
}

# --------------------------------------------------------------------------
# 4. TYPE (Loại năng lượng)
# --------------------------------------------------------------------------
TYPE_VN = {
    "Manifestor": "Người khởi xướng",
    "Generator": "Người tạo năng lượng",
    "Manifesting Generator": "Người tạo năng lượng biểu hiện",
    "Projector": "Người định hướng",
    "Reflector": "Người phản chiếu",
}

# --------------------------------------------------------------------------
# 5. TRẠNG THÁI CẢM XÚC (Not-Self / Chữ ký)
# --------------------------------------------------------------------------
NOT_SELF_SIGNATURE = {
    "Manifestor": ("Tức giận (khi bị ngăn cản)", "Bình an"),
    "Generator": ("Thất vọng (khi làm điều không muốn)", "Thỏa mãn"),
    "Manifesting Generator": ("Thất vọng và tức giận", "Thỏa mãn và bình an"),
    "Projector": ("Cay đắng (khi không được mời)", "Thành công"),
    "Reflector": ("Thất vọng (khi bị ép phải nhanh)", "Ngạc nhiên thích thú"),
}

# --------------------------------------------------------------------------
# 6. TRUNG TÂM NĂNG LƯỢNG — theo knowledge/02_9_trung_tam.md
# --------------------------------------------------------------------------
CENTER_VN = {
    "Head": "Trung tâm Đầu",
    "Ajna": "Trung tâm Ajna",
    "Throat": "Trung tâm Họng",
    "G": "Trung tâm G (Bản ngã)",
    "Heart": "Trung tâm Tim",
    "Spleen": "Trung tâm Lá Lách",
    "Sacral": "Trung tâm Xương Cùng",
    "Solar Plexus": "Đám rối Thái Dương",
    "Root": "Trung tâm Gốc",
}

# --------------------------------------------------------------------------
# 7. NHÃN GIAO DIỆN
# --------------------------------------------------------------------------
UI = {
    "strategy": "CHIẾN LƯỢC SỐNG",
    "authority": "QUYỀN NỘI TẠI",
    "definition": "ĐỊNH NGHĨA",
    "profile": "NHÂN CÁCH",
    "cross": "CHỮ THẬP HÓA THÂN",
    "type": "LOẠI NĂNG LƯỢNG",
    "not_self": "KHI SỐNG SAI THIẾT KẾ",
    "signature": "DẤU HIỆU SỐNG ĐÚNG",
    "strength": "ĐIỂM MẠNH (TÀI NĂNG CỐ ĐỊNH)",
    "blindspot": "ĐIỂM MÙ (BÀI HỌC TRÍ TUỆ)",
    "activated_gates": "CỔNG ĐANG KÍCH HOẠT",
    "def_channels": "KÊNH ĐỊNH NGHĨA",
    "def_centers": "TRUNG TÂM ĐỊNH NGHĨA",
    "hanging_gates": "CỔNG TREO",
    "open_hint": "Trắng = nơi bạn dễ bị ảnh hưởng, cũng là nơi học được trí tuệ",
    "defined_hint": "Có màu = năng lượng cố định, tài năng bẩm sinh",
}


def _vn_part(raw):
    """Tách phần tiếng Việt trong chuỗi 'EN - VN' của hd_calculator."""
    if not raw:
        return ""
    txt = str(raw)
    for sep in (" - ", " – ", " — "):
        if sep in txt:
            head, tail = txt.split(sep, 1)
            # phần nào chứa ký tự có dấu thì là tiếng Việt
            if any(ord(c) > 127 for c in tail):
                return tail.strip()
            return head.strip()
    return txt.strip()


def vn_strategy(raw, hd_type=None):
    """Chiến lược tiếng Việt đã trau chuốt (ưu tiên tra theo Type)."""
    if hd_type and hd_type in STRATEGY_VN:
        return STRATEGY_VN[hd_type]
    part = _vn_part(raw)
    return part if part else str(raw or "")


def vn_authority(raw):
    if not raw:
        return ""
    key = str(raw).strip()
    if key in AUTHORITY_VN:
        return AUTHORITY_VN[key]
    low = key.lower()
    for k, v in AUTHORITY_VN.items():
        if k.lower() in low:
            return v
    return _title_sentence(key)


def vn_definition(raw):
    if not raw:
        return ""
    key = str(raw).strip()
    if key in DEFINITION_VN:
        return DEFINITION_VN[key]
    if key.endswith("Splits"):
        return f"Định nghĩa chia {key.split()[0].lower()}"
    for k, v in DEFINITION_VN.items():
        if k.split()[0].lower() in key.lower():
            return v
    return _title_sentence(key)


def vn_type(raw, gloss=False):
    name = str(raw or "").strip()
    if gloss and name in TYPE_VN:
        return f"{name} · {TYPE_VN[name]}"
    return name


def vn_center(raw):
    key = str(raw or "").strip()
    return CENTER_VN.get(key, _title_sentence(key))


def _title_sentence(s):
    """Chỉ viết hoa chữ đầu — tránh kiểu Title Case dịch thô."""
    s = " ".join(str(s).split())
    if not s:
        return s
    return s[0].upper() + s[1:]


if __name__ == "__main__":
    tests = ["Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo",
             "Wait for the Invitation - Chờ Lời Mời",
             "Inform - Thông Báo trước khi hành động",
             "Emotional - Solar Plexus", "Split Definition", "Manifesting Generator"]
    for t in tests:
        print(f"{t!r:70} -> {vn_strategy(t, 'Projector') if 'Invitation' in t else (vn_authority(t) if 'Plexus' in t or 'Split' in t else vn_strategy(t))}")

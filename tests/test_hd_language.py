"""Tests for the shared Vietnamese terminology layer (tools/hd_language.py).

Mọi nơi hiển thị phải dùng cùng bộ thuật ngữ trau chuốt này — không chuỗi
song ngữ thô kiểu "Chờ Đáp Ứng rồi Thông Báo".
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))

import hd_language as hd  # noqa: E402


def test_strategy_polished_by_type():
    assert hd.vn_strategy("Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo",
                          "Manifesting Generator") == "Chờ phản hồi rồi thông báo"
    assert hd.vn_strategy("Wait for the Invitation - Chờ Lời Mời", "Projector") == "Chờ lời mời"
    assert hd.vn_strategy("Inform - Thông Báo trước khi hành động",
                          "Manifestor") == "Thông báo trước khi hành động"


def test_authority_polished_terms():
    assert hd.vn_authority("Emotional - Solar Plexus") == "Quyền Cảm xúc — Đám rối Thái Dương"
    assert (
        hd.vn_authority("Mental - Environment / No Inner Authority")
        == "Dựa vào môi trường — không có quyền nội tại"
    )
    assert hd.vn_authority("Ego (Heart)") == "Quyền Bản ngã — Tim"


def test_definition_polished_terms():
    assert hd.vn_definition("Split Definition") == "Định nghĩa chia tách (hai khối)"
    assert hd.vn_definition("Single Definition") == "Định nghĩa đơn (một khối liền)"


def test_type_gloss_pairs_term_with_life_name():
    assert hd.vn_type("Projector", gloss=True) == "Projector · Người định hướng"
    assert hd.vn_type("Generator") == "Generator"


def test_center_names_follow_knowledge_base():
    assert hd.vn_center("Solar Plexus") == "Đám rối Thái Dương"
    assert hd.vn_center("Spleen") == "Trung tâm Lá Lách"
    assert hd.vn_center("Sacral") == "Trung tâm Xương Cùng"


def test_not_self_signature_pairs():
    assert hd.NOT_SELF_SIGNATURE["Projector"] == ("Cay đắng (khi không được mời)", "Thành công")
    assert hd.NOT_SELF_SIGNATURE["Manifestor"] == ("Tức giận (khi bị ngăn cản)", "Bình an")


def test_unknown_terms_degrade_gracefully():
    assert hd.vn_definition("") == ""
    assert hd.vn_center("Unknown Center") == "Unknown Center"

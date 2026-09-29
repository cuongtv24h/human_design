"""Pipeline đóng góp tri thức (A–C): sàng lọc → hàng chờ duyệt → xuất kho.

- Sàng lọc tự động khi nộp: heading, dung lượng, lộ bí mật (RAG-poisoning),
  trùng ≥90% → 422 KHÔNG lưu.
- Coach chỉ nộp/đọc bài của mình; Admin duyệt (approve xuất kho atomic +
  ghi sổ nguồn) / reject lý do / AI review / stats / dedupe-scan.
- Test KHÔNG BAO GIỜ ghi knowledge/ thật: monkeypatch module paths về tmp.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fastapi.testclient import TestClient  # noqa: E402

from backend.api import assistant_tools, kb_pipeline  # noqa: E402
from backend.api.models import KnowledgeSubmission  # noqa: E402
from tests.test_knowledge_search import (  # noqa: E402
    H,
    PASSWORD,
    _login_coach,
    app,
    login,
)

REAL_KNOWLEDGE = ROOT / "knowledge"
REAL_DOCS = ROOT / "docs"
GOOD = """# Khoai tây bắt buộc cho luồng máy

## Cánh đồng zorblax quantum
Nội dung thử nghiệm độc nhất về luồng gió máy trottingsoxel vô điều kiện,
không lặp lại bất kỳ đoạn nào đã có trong kho tri thức hiện tại.
"""


@pytest.fixture()
def kb_env(tmp_path, monkeypatch):
    """Corpus + sổ nguồn COPY sang tmp — publish không được chạm file thật."""
    kn = tmp_path / "knowledge"
    docs = tmp_path / "docs"
    shutil.copytree(REAL_KNOWLEDGE, kn)
    shutil.copytree(REAL_DOCS, docs)
    src = docs / "KNOWLEDGE_SOURCES.md"
    monkeypatch.setattr(assistant_tools, "KNOWLEDGE_DIR", kn)
    monkeypatch.setattr(assistant_tools, "DOCS_DIR", docs)
    monkeypatch.setattr(kb_pipeline, "KNOWLEDGE_DIR", kn)
    monkeypatch.setattr(kb_pipeline, "SOURCES_FILE", src)
    return kn, docs, src


def _db(app_) -> object:
    """Database (không phải Session) — mở session_factory() trực tiếp trong helper."""
    return app_.state.db


def _count(db) -> int:
    with db.session_factory() as s:
        return s.query(KnowledgeSubmission).count()


def _statuses(db) -> list[str]:
    with db.session_factory() as s:
        return [st for (st,) in s.query(KnowledgeSubmission.status).all()]


def test_submit_screen_rejects_hard_cases_without_saving(app, kb_env):
    """Secret/hết heading/quá lớn/trùng ≥90% → 422 và KHÔNG có row nào."""
    coach = _login_coach(app)
    db = _db(app)

    secret = GOOD + "\napi_key = 'abcdefghijklmnop123456'\n"
    no_heading = "văn bản thuần không có heading gì cả."
    oversize = "# Tiêu đề\n\n## Phần\n" + "x" * 61_000
    cases = [
        {"title": "Lộ bí mật", "content_md": secret},
        {"title": "Hết heading", "content_md": no_heading},
        {"title": "Quá lớn", "content_md": oversize},
        {"title": "Đích xấu", "content_md": GOOD, "target_file": "../../evil.md"},
    ]
    for payload in cases:
        resp = coach.post("/api/v1/knowledge/submissions", json=payload, headers=H)
        assert resp.status_code == 422, (payload["title"], resp.text)
    assert _count(db) == 0

    # Nộp hợp lệ lần 1 → 201; nộp y hệt lần 2 → trùng cứng 422, vẫn chỉ 1 row.
    ok = coach.post("/api/v1/knowledge/submissions",
                    json={"title": "Bài chuẩn", "content_md": GOOD}, headers=H)
    assert ok.status_code == 201, ok.text
    dup = coach.post("/api/v1/knowledge/submissions",
                     json={"title": "Bài trùng", "content_md": GOOD + "\n## Phần phụ\n\nThêm một dòng."},
                     headers=H)
    assert dup.status_code == 422, dup.text
    assert "trùng lặp" in dup.json()["detail"].lower()
    assert _count(db) == 1
    with db.session_factory() as s:
        row = s.query(KnowledgeSubmission).one()
    assert row.status == "pending" and row.dedupe_report["level"] in {"none", "soft"}


def test_roles_list_detail_and_status_filter(app, kb_env):
    """Anon 401; coach chỉ thấy bài của mình + không duyệt được; admin thấy tất cả."""
    anon = TestClient(app)
    assert anon.get("/api/v1/knowledge/submissions", headers=H).status_code == 401
    assert anon.post("/api/v1/knowledge/submissions", json={}, headers=H).status_code == 401

    coach = _login_coach(app)
    admin = login(app)
    r1 = coach.post("/api/v1/knowledge/submissions",
                    json={"title": "Bài của coach", "content_md": GOOD}, headers=H)
    assert r1.status_code == 201, r1.text
    sub1 = r1.json()["id"]
    content2 = GOOD.replace("zorblax", "blaxxor")
    r2 = coach.post("/api/v1/knowledge/submissions",
                    json={"title": "Bài thứ hai", "content_md": content2}, headers=H)
    assert r2.status_code == 201, r2.text
    sub2 = r2.json()["id"]
    # Admin cũng tự đóng góp được (vẫn qua sàng lọc).
    r3 = admin.post("/api/v1/knowledge/submissions",
                    json={"title": "Bài của admin", "content_md": GOOD.replace("zorblax", "xorbazz")},
                    headers=H)
    assert r3.status_code == 201, r3.text
    sub3 = r3.json()["id"]

    coach_list = coach.get("/api/v1/knowledge/submissions", headers=H).json()
    assert coach_list["total"] == 2
    admin_list = admin.get("/api/v1/knowledge/submissions", headers=H).json()
    assert admin_list["total"] == 3
    pending = admin.get("/api/v1/knowledge/submissions", params={"status": "pending"},
                        headers=H).json()
    assert pending["total"] == 3
    bad_filter = admin.get("/api/v1/knowledge/submissions", params={"status": "draft"}, headers=H)
    assert bad_filter.status_code == 422

    # Detail: own-or-admin — coach không đọc được bài của admin.
    assert coach.get(f"/api/v1/knowledge/submissions/{sub1}", headers=H).status_code == 200
    assert coach.get(f"/api/v1/knowledge/submissions/{sub3}", headers=H).status_code == 404
    detail = admin.get(f"/api/v1/knowledge/submissions/{sub1}", headers=H).json()
    assert detail["can_review"] is True and "preview" in detail
    assert detail["contributor"]

    # Reject → lý do hiện với coach; coach không có quyền duyệt/tính năng admin.
    rej = admin.post(f"/api/v1/knowledge/submissions/{sub2}/reject",
                     json={"reason": "Nội dung chưa đủ nguồn tham chiếu."}, headers=H)
    assert rej.status_code == 200, rej.text
    assert rej.json()["status"] == "rejected"
    seen = coach.get(f"/api/v1/knowledge/submissions/{sub2}", headers=H).json()
    assert seen["reject_reason"] and seen["status"] == "rejected"

    for method, path in (
        ("post", f"/api/v1/knowledge/submissions/{sub1}/approve"),
        ("post", f"/api/v1/knowledge/submissions/{sub2}/reject"),
        ("post", f"/api/v1/knowledge/submissions/{sub1}/ai-review"),
        ("get", "/api/v1/knowledge/stats"),
        ("post", "/api/v1/knowledge/dedupe-scan"),
    ):
        if method == "post":
            body = {"reason": "x"} if path.endswith("/reject") else {}
            resp = coach.post(path, json=body, headers=H)
        else:
            resp = coach.get(path, headers=H)
        assert resp.status_code == 403, (path, resp.status_code)
    assert anon.get("/api/v1/knowledge/stats", headers=H).status_code == 401

    # Admin quyết định: approve đã reject → 422 (hết pending).
    again = admin.post(f"/api/v1/knowledge/submissions/{sub2}/approve", json={}, headers=H)
    assert again.status_code == 422


def test_approve_publishes_appends_sources_and_searchable(app, kb_env):
    """Duyệt → file md xuất hiện (tạo mới + append file có sẵn) + sổ nguồn +
    search NGAY sees + duyệt lại 422."""
    kn, docs, src = kb_env
    coach = _login_coach(app)
    admin = login(app)
    db = _db(app)

    # 1) Tạo file mới (không chỉ định target).
    r1 = coach.post("/api/v1/knowledge/submissions",
                    json={"title": "Khoai tây bắt buộc", "content_md": GOOD}, headers=H)
    assert r1.status_code == 201
    sub1 = r1.json()["id"]
    ap1 = admin.post(f"/api/v1/knowledge/submissions/{sub1}/approve", json={}, headers=H)
    assert ap1.status_code == 200, ap1.text
    pub = ap1.json()["published"]
    assert pub["mode"] == "create"
    new_file = kn / pub["file"]
    assert new_file.is_file() and "# Khoai tây bắt buộc" in new_file.read_text(encoding="utf-8")
    # Sổ nguồn: đợt mới "Đóng góp nội bộ" trỏ đúng file đích.
    src_text = src.read_text(encoding="utf-8")
    assert "Đóng góp nội bộ" in src_text and pub["file"] in src_text
    # Search thấy NGAY (fingerprint cache tự invalidate).
    hits = assistant_tools.search_knowledge_hits("khoai tay bat buoc zorblax", top_k=10)
    assert any(h["file"] == pub["file"] for h in hits), [h["file"] for h in hits]
    # Duyệt lại → 422.
    assert admin.post(f"/api/v1/knowledge/submissions/{sub1}/approve",
                      json={}, headers=H).status_code == 422
    # Nộp trùng bài vừa xuất → trùng cứng (corpus đã có file mới).
    dup = coach.post("/api/v1/knowledge/submissions",
                     json={"title": "Trùng bài đã duyệt", "content_md": GOOD}, headers=H)
    assert dup.status_code == 422, dup.text

    # 2) Append vào file có sẵn: Admin sửa nội dung lúc duyệt (override content_md).
    existing = sorted(p.name for p in kn.glob("0*.md"))[0]
    content2 = GOOD.replace("zorblax", "wibbleflux")
    r2 = coach.post("/api/v1/knowledge/submissions",
                    json={"title": "Bổ sung phần mới", "content_md": content2,
                          "target_file": existing}, headers=H)
    assert r2.status_code == 201
    sub2 = r2.json()["id"]
    edited = content2.replace("wibbleflux", "editedbyadmin")
    ap2 = admin.post(f"/api/v1/knowledge/submissions/{sub2}/approve",
                     json={"content_md": edited}, headers=H)
    assert ap2.status_code == 200, ap2.text
    assert ap2.json()["published"] == {"file": existing, "mode": "append"}
    body = (kn / existing).read_text(encoding="utf-8")
    assert "## Cánh đồng" in body and "editedbyadmin" in body
    # Trạng thái cuối.
    assert sorted(_statuses(db)) == ["approved", "approved"]


def test_ai_review_stats_and_scan(app, kb_env, monkeypatch):
    """Phase B (AI on-demand, lỗi không chặn) + Phase C (stats + dedupe-scan)."""
    coach = _login_coach(app)
    admin = login(app)
    db = _db(app)
    r = coach.post("/api/v1/knowledge/submissions",
                   json={"title": "Bài chờ AI", "content_md": GOOD}, headers=H)
    sub_id = r.json()["id"]

    # Happy path: giả lập LLM trả JSON kiểm duyệt.
    monkeypatch.setattr(
        "backend.api.services.org_llm_configs", lambda d, org, sec: [object()]
    )
    monkeypatch.setattr(
        "backend.api.services.save_llm_usages", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "backend.reporting.llm_client.call_llm_with_usage",
        lambda brief, config, transport=None, system=None: (
            {"mâu thuẫn": "không", "trùng ý": "không", "ghi chú": "Chất lượng ổn."},
            {"prompt_tokens": 10, "completion_tokens": 5},
        ),
    )
    ai = admin.post(f"/api/v1/knowledge/submissions/{sub_id}/ai-review", headers=H)
    assert ai.status_code == 200, ai.text
    body = ai.json()
    assert body["ran"] is True and body["ai_notes"]["ghi chú"]
    item = admin.get(f"/api/v1/knowledge/submissions/{sub_id}", headers=H).json()
    assert item["ai_notes"]["ghi chú"] == "Chất lượng ổn."

    # LLM lỗi → ran:false, ai_notes không bị ghi đè, duyệt vẫn chạy được.
    from backend.reporting.llm_client import LLMError

    def _boom(*a, **k):
        raise LLMError("mạng chập chờn")

    monkeypatch.setattr("backend.reporting.llm_client.call_llm_with_usage", _boom)
    ai2 = admin.post(f"/api/v1/knowledge/submissions/{sub_id}/ai-review", headers=H)
    assert ai2.status_code == 200 and ai2.json()["ran"] is False
    assert ai2.json()["error"]
    assert admin.post(f"/api/v1/knowledge/submissions/{sub_id}/approve",
                      json={}, headers=H).status_code == 200

    # Stats: shape + số liệu phản ánh DB.
    stats = admin.get("/api/v1/knowledge/stats", headers=H).json()
    assert set(stats["submissions"]) == {"pending", "approved", "rejected", "total"}
    assert stats["submissions"]["approved"] == 1 and stats["submissions"]["pending"] == 0
    assert set(stats["queries_30d"]) == {"total", "avg_took_ms", "top"}

    # Dedupe scan: quét toàn bộ cặp ≥0.70, top ≤20, không có cặp trùng chính nó.
    scan = admin.post("/api/v1/knowledge/dedupe-scan", headers=H)
    assert scan.status_code == 200, scan.text
    data = scan.json()
    assert data["chunks"] >= 100 and "duration_ms" in data
    assert 0 <= len(data["pairs"]) <= 20
    for pair in data["pairs"]:
        assert pair["similarity"] >= 0.7
        assert pair["a"]["file"] != pair["b"]["file"] or pair["a"]["section"] != pair["b"]["section"]


def _uniq_content(tag: str) -> str:
    """Nội dung khác biệt hoàn toàn theo tag — không dính hard-dup khi test cap."""
    body = " ".join(f"{tag}no{i}x" for i in range(30))
    return (f"# Tieu de {tag}\n\n## Muc rieng {tag}\n"
            f"Noi dung rieng biet {body} de khong trung voi cac bai khac trong luong.\n")


def test_source_url_scheme_and_title_reason_validation(app, kb_env):
    """Audit M1+M2+L1: chặn javascript:/data:/ftp (click-XSS), title xuống dòng
    (injection heading vào sổ nguồn), title/reason toàn khoảng trắng."""
    coach = _login_coach(app)
    admin = login(app)
    db = _db(app)

    for i, bad in enumerate(("javascript:alert(1)", "data:text/html,<b>x</b>",
                             "ftp://x.com/f", "https://", "JaVaScRiPt:alert(1)")):
        r = coach.post("/api/v1/knowledge/submissions",
                       json={"title": f"URL test {i}", "content_md": _uniq_content(f"urlbad{i}"),
                             "source_url": bad}, headers=H)
        assert r.status_code == 422, (bad, r.text)
    assert _count(db) == 0

    good_url = coach.post("/api/v1/knowledge/submissions",
                          json={"title": "URL hop le", "content_md": _uniq_content("urlgood"),
                                "source_url": "https://example.com/bai-viet"}, headers=H)
    assert good_url.status_code == 201, good_url.text

    # title chứa newline (đã từng chèn được heading giả vào KNOWLEDGE_SOURCES.md)
    r_nl = coach.post("/api/v1/knowledge/submissions",
                      json={"title": "Hop le\n## Doi gia", "content_md": _uniq_content("nl")}, headers=H)
    assert r_nl.status_code == 422 and "điều khiển" in r_nl.json()["detail"]
    # title toàn khoảng trắng
    r_ws = coach.post("/api/v1/knowledge/submissions",
                      json={"title": "   ", "content_md": _uniq_content("ws")}, headers=H)
    assert r_ws.status_code == 422
    assert _count(db) == 1

    # reject reason toàn khoảng trắng → 422, bài vẫn pending
    sid = good_url.json()["id"]
    r_rj = admin.post(f"/api/v1/knowledge/submissions/{sid}/reject",
                      json={"reason": "  "}, headers=H)
    assert r_rj.status_code == 422
    detail = admin.get(f"/api/v1/knowledge/submissions/{sid}", headers=H).json()
    assert detail["status"] == "pending"


def test_pending_cap_per_user(app, kb_env):
    """Audit L2: ≤5 bài pending/người — nộp thứ 6 →422; duyệt1 bài là có slot."""
    coach = _login_coach(app)
    admin = login(app)
    for i in range(kb_pipeline.MAX_PENDING_PER_USER):
        r = coach.post("/api/v1/knowledge/submissions",
                       json={"title": f"Bai {i}", "content_md": _uniq_content(f"cap{i}")}, headers=H)
        assert r.status_code == 201, (i, r.text)
    over = coach.post("/api/v1/knowledge/submissions",
                      json={"title": "Bai thu 6", "content_md": _uniq_content("capover")}, headers=H)
    assert over.status_code == 422 and "chờ duyệt" in over.json()["detail"]

    # Admin duyệt1 bài → nhả slot → nộp được again
    items = admin.get("/api/v1/knowledge/submissions", params={"status": "pending"},
                      headers=H).json()["items"]
    assert len(items) == kb_pipeline.MAX_PENDING_PER_USER
    ap = admin.post(f"/api/v1/knowledge/submissions/{items[0]['id']}/approve",
                    json={}, headers=H)
    assert ap.status_code == 200, ap.text
    again = coach.post("/api/v1/knowledge/submissions",
                       json={"title": "Sau khi duyet", "content_md": _uniq_content("capagain")}, headers=H)
    assert again.status_code == 201, again.text

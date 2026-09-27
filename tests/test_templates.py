"""API mẫu báo cáo Giai đoạn 1: khối, mẫu, workflow duyệt, thư viện chung."""

from test_api_v1 import CLIENT, H, PASSWORD, app, login  # noqa: F401  (tái dùng fixture app)

BLOCK = {"name": "Lời chào riêng",
         "body": "Xin chào {{subject.name}}, nhóm {{subject.type_vn}}! Hotline {{org.hotline}}."}


def _mkblock(c, body=None):
    r = c.post("/api/v1/templates/blocks", json=body or BLOCK, headers=H)
    assert r.status_code == 201, r.text
    return r.json()


def _mktpl(c, sections, **kw):
    payload = {"name": kw.pop("name", "Mẫu test"), "sections": sections, **kw}
    r = c.post("/api/v1/templates", json=payload, headers=H)
    assert r.status_code == 201, r.text
    return r.json()


def _coach(app, admin, email):
    r = admin.post("/api/v1/users",
                   json={"email": email, "full_name": "Coach", "password": PASSWORD, "role": "coach"},
                   headers=H)
    assert r.status_code == 201, r.text
    return login(app, email)


def test_block_crud_and_usage_guard(app):
    c = login(app)
    blk = _mkblock(c)
    assert set(blk["variables"]) == {"subject.name", "subject.type_vn", "org.hotline"}

    r = c.patch(f"/api/v1/templates/blocks/{blk['id']}", json={"name": "Chào"}, headers=H)
    assert r.status_code == 200 and r.json()["name"] == "Chào"

    tpl = _mktpl(c, [{"type": "block", "block_id": blk["id"]}])
    r = c.delete(f"/api/v1/templates/blocks/{blk['id']}", headers=H)
    assert r.status_code == 409 and tpl["name"] in r.json()["detail"]

    assert c.delete(f"/api/v1/templates/{tpl['id']}", headers=H).status_code == 204
    assert c.delete(f"/api/v1/templates/blocks/{blk['id']}", headers=H).status_code == 204


def test_template_workflow_coach_submit_admin_approve(app):
    c = login(app)
    coach = _coach(app, c, "coach-tpl@demo.vn")

    blk = _mkblock(coach)
    tpl = _mktpl(coach, [{"type": "builtin", "ref": "summary"},
                          {"type": "block", "block_id": blk["id"], "title_override": "Chào bạn"}])
    assert tpl["status"] == "draft" and tpl["key"].startswith("mau-test")
    tid = tpl["id"]

    # coach không tự duyệt
    r = coach.patch(f"/api/v1/templates/{tid}", json={"status": "active"}, headers=H)
    assert r.status_code == 403
    # gửi duyệt
    r = coach.patch(f"/api/v1/templates/{tid}", json={"status": "pending"}, headers=H)
    assert r.status_code == 200 and r.json()["status"] == "pending"
    # coach khác không thấy bản nháp của người khác
    coach2 = _coach(app, c, "coach2-tpl@demo.vn")
    assert coach2.get(f"/api/v1/templates/{tid}").status_code == 404

    # từ chối thiếu lý do -> 422
    r = c.patch(f"/api/v1/templates/{tid}", json={"status": "rejected"}, headers=H)
    assert r.status_code == 422
    r = c.patch(f"/api/v1/templates/{tid}", json={"status": "rejected", "review_note": "Thiếu mục CTA"},
                headers=H)
    assert r.status_code == 200 and r.json()["review_note"] == "Thiếu mục CTA"

    # coach sửa rồi gửi lại, admin duyệt
    assert coach.patch(f"/api/v1/templates/{tid}", json={"description": "Đã bổ sung"}, headers=H).status_code == 200
    assert coach.patch(f"/api/v1/templates/{tid}", json={"status": "pending"}, headers=H).status_code == 200
    r = c.patch(f"/api/v1/templates/{tid}", json={"status": "active"}, headers=H)
    assert r.status_code == 200 and r.json()["status"] == "active"

    got = c.get(f"/api/v1/templates/{tid}").json()
    assert got["sections"][0]["ref"] == "summary" and got["sections"][1]["title"] == "Chào bạn"


def test_template_validation(app):
    c = login(app)
    bad = {"name": "X", "sections": [{"type": "builtin", "ref": "khong-co"}]}
    assert c.post("/api/v1/templates", json=bad, headers=H).status_code == 422
    bad = {"name": "X", "sections": []}
    assert c.post("/api/v1/templates", json=bad, headers=H).status_code == 422
    bad = {"name": "X", "sections": [{"type": "block", "block_id": 99999}]}
    assert c.post("/api/v1/templates", json=bad, headers=H).status_code == 422


def test_from_builtin_duplicate_and_samples(app):
    c = login(app)
    r = c.post("/api/v1/templates/from-builtin", json={"builtin": "sections", "name": "Từ hệ thống"},
               headers=H)
    assert r.status_code == 201, r.text
    tid = r.json()["id"]
    from backend.reporting.catalog import CORE_SECTIONS
    assert [s["ref"] for s in r.json()["sections"]] == [s.id for s in CORE_SECTIONS]

    r = c.post(f"/api/v1/templates/{tid}/duplicate", json={"name": "Bản sao"}, headers=H)
    assert r.status_code == 201 and r.json()["status"] == "draft"

    s = c.post(f"/api/v1/templates/{tid}/samples", json={"title": "Bài hay", "body": "Mở bài " * 50},
               headers=H).json()
    assert s["title"] == "Bài hay"
    r = c.patch(f"/api/v1/templates/{tid}", json={"status": "pending"}, headers=H)
    assert r.json()["samples_count"] == 1
    assert c.delete(f"/api/v1/templates/samples/{s['id']}", headers=H).status_code == 204


def test_org_vars(app):
    c = login(app)
    coach = _coach(app, c, "coach-vars@demo.vn")
    assert coach.get("/api/v1/templates/org-vars").status_code == 403
    r = c.put("/api/v1/templates/org-vars",
              json={"vars": [{"key": "hotline", "value": "1900 1", "label": "Hotline"}]}, headers=H)
    assert r.status_code == 200 and r.json()["vars"][0]["key"] == "hotline"
    bad = {"vars": [{"key": "a", "value": "1"}, {"key": "a", "value": "2"}]}
    assert c.put("/api/v1/templates/org-vars", json=bad, headers=H).status_code == 422
    bad = {"vars": [{"key": "Hot Line!", "value": "1"}]}
    assert c.put("/api/v1/templates/org-vars", json=bad, headers=H).status_code == 422


def test_publish_library_import(app):
    c = login(app)
    tpl = _mktpl(c, [{"type": "builtin", "ref": "summary"}])
    # chưa duyệt thì không chia sẻ được
    assert c.post(f"/api/v1/templates/{tpl['id']}/publish", headers=H).status_code == 422
    c.patch(f"/api/v1/templates/{tpl['id']}", json={"status": "active"}, headers=H)

    r = c.post(f"/api/v1/templates/{tpl['id']}/publish",
               json={"badge": "Chính chủ", "origin_label": "Demo Studio"}, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["visibility"] == "shared" and r.json()["badge"] == "Chính chủ"

    lib = c.get("/api/v1/templates/library").json()
    assert any(t["key"] == tpl["key"] and t["import_count"] == 0 for t in lib)
    # lấy về studio của chính mình bị chặn
    assert c.post(f"/api/v1/templates/library/{tpl['key']}/import", headers=H).status_code == 422
    # nhân bản thành nháp riêng vẫn được
    other = _mktpl(c, [{"type": "builtin", "ref": "summary"}], name="X")
    dup = c.post(f"/api/v1/templates/{other['id']}/duplicate", headers=H).json()
    assert dup["visibility"] == "private" and dup["status"] == "draft"

    assert c.post(f"/api/v1/templates/{tpl['id']}/unpublish", headers=H).status_code == 204
    lib = c.get("/api/v1/templates/library").json()
    assert all(t["key"] != tpl["key"] for t in lib)


def test_custom_report_end_to_end(app):
    c = login(app)
    c.put("/api/v1/templates/org-vars", json={"vars": [{"key": "hotline", "value": "1900 6868"}]},
          headers=H)
    blk = _mkblock(c)
    tpl = _mktpl(c, [{"type": "builtin", "ref": "summary"}, {"type": "block", "block_id": blk["id"]}])
    c.patch(f"/api/v1/templates/{tpl['id']}", json={"status": "active"}, headers=H)

    # catalog có mẫu custom
    cat = c.get("/api/v1/catalog").json()
    assert any(t["value"] == tpl["key"] and t["badge"] == "Studio" for t in cat["templates"])

    # xem trước mẫu chạy orchestrator thật
    r = c.post("/api/v1/templates/preview", json={"template_id": tpl["id"]}, headers=H)
    assert r.status_code == 200, r.text
    assert any("1900 6868" in (s.get("markdown") or "") for s in r.json()["sections"])

    # tạo báo cáo thật bằng mẫu custom
    cid = c.post("/api/v1/clients", json=CLIENT, headers=H).json()["id"]
    payload = {"client_id": cid, "tier": "deep_core", "template": tpl["key"],
               "content_mode": "template", "domains": ["money"]}
    r = c.post("/api/v1/reports/preview", json=payload, headers=H)
    assert r.status_code == 200, r.text
    assert r.json()["sections"][1]["title"] == "Lời chào riêng"

    r = c.post("/api/v1/reports", json=payload, headers=H)
    assert r.status_code == 201, r.text
    got = c.get(f"/api/v1/reports/{r.json()['id']}").json()
    assert got["template_name"] == tpl["name"] and len(got["sections"]) == 3
    assert "1900 6868" in got["markdown"] and "Nguyễn Văn A" in got["markdown"]

    # mẫu không tồn tại -> 422
    bad = dict(payload, template="mau-khong-co")
    assert c.post("/api/v1/reports/preview", json=bad, headers=H).status_code == 422
    assert c.post("/api/v1/reports", json=bad, headers=H).status_code == 422

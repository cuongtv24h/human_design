"""API tra cứu tri thức: search_knowledge_hits (không đổi tool chatbot) + /knowledge.*."""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fastapi.testclient import TestClient  # noqa: E402

from backend.api.assistant_tools import (  # noqa: E402
    docs_chunks,
    knowledge_chunks,
    search_knowledge,
    search_knowledge_hits,
)
from backend.api.cli import ensure_admin  # noqa: E402
from backend.api.main import create_app  # noqa: E402
from backend.api.settings import Settings  # noqa: E402

H = {"X-HD-Request": "1"}
PASSWORD = "matkhau-123"
QUERIES = ["manifesting generator", "nuôi dạy con", "BodyGraph trung tâm"]


@pytest.fixture()
def app(tmp_path):
    application = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'api.sqlite3'}",
                                      artifact_dir=str(tmp_path / "artifacts"), secret_key="test-secret"))
    ensure_admin(application.state.db, "admin@example.com", PASSWORD, "Quản trị")
    return application


def login(app) -> TestClient:
    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD},
                           headers=H)
    assert response.status_code == 200, response.text
    return client


def test_tool_output_is_join_of_hits():
    """Chatbot tool = join các hit: cùng scoring, cùng snippet, cùng thứ tự nguồn."""
    for q in QUERIES:
        text, sources = search_knowledge(q, top_k=3)
        hits = search_knowledge_hits(q, top_k=3, source="knowledge")
        assert hits, f"query {q!r} không có hit"
        expected = "\n\n---\n\n".join(f"[{h['title']} — {h['file']}]\n{h['snippet']}" for h in hits)
        assert text == expected
        titles: list[str] = []
        for h in hits:
            if h["title"] not in titles:
                titles.append(h["title"])
        assert sources == "Kho kiến thức: " + "; ".join(titles)


def test_short_query_returns_empty_hits():
    assert search_knowledge("của")[0].startswith("Từ khóa quá ngắn")
    assert search_knowledge_hits("của") == []


def test_hit_shape_and_scores_sorted():
    hits = search_knowledge_hits("manifesting generator sacral", top_k=5, source="all")
    assert hits
    for hit in hits:
        assert set(hit) == {"file", "title", "section", "source", "score", "snippet", "text"}
        assert hit["source"] in {"knowledge", "docs"}
        assert hit["snippet"] and hit["text"]
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_docs_source_is_whitelisted_and_tagged():
    hits = search_knowledge_hits("BodyGraph cấu trúc", top_k=10, source="docs")
    assert hits, "wiki BodyGraph phải có hit"
    for hit in hits:
        assert hit["source"] == "docs"
        name = hit["file"]
        assert name.startswith(("Wiki Phân mục", "Báo cáo Wiki Tổng quan")) or \
            name in {"KNOWLEDGE_SOURCES.md", "NARRATIVE_STANDARD.md", "REPORTING_ARCHITECTURE.md"}
    # file hạ tầng/meta không được tham gia tra cứu
    blocked = {"DEPLOY_VPS.md", "SUPABASE_DB.md", "README.md", "GAME_ASSET_BRIEF.md"}
    assert blocked.isdisjoint({hit["file"] for hit in hits})
    assert blocked.isdisjoint({f for f, _, _ in docs_chunks()})


def test_knowledge_source_excludes_docs():
    hits = search_knowledge_hits("nuôi dạy con", top_k=10, source="knowledge")
    assert hits
    docs_files = {f for f, _, _ in docs_chunks()}
    assert docs_files.isdisjoint({h["file"] for h in hits})


def test_file_filter():
    hits = search_knowledge_hits("nuôi dạy con", top_k=5, source="knowledge")
    target = hits[0]["file"]
    filtered = search_knowledge_hits("nuôi dạy con", top_k=20, source="all", file=target)
    assert filtered and all(h["file"] == target for h in filtered)


def test_knowledge_chunks_cache_stable():
    assert knowledge_chunks() == knowledge_chunks()
    assert len(knowledge_chunks()) >= 200
    assert len(docs_chunks()) >= 50


def test_api_requires_auth(app):
    anon = TestClient(app)
    assert anon.get("/api/v1/knowledge/search?q=BodyGraph", headers=H).status_code == 401
    assert anon.get("/api/v1/knowledge/files", headers=H).status_code == 401


def test_api_search_and_validation(app):
    client = login(app)
    ok = client.get("/api/v1/knowledge/search?q=manifesting+generator&limit=5", headers=H)
    assert ok.status_code == 200, ok.text
    body = ok.json()
    assert body["query"] == "manifesting generator"
    assert 1 <= len(body["hits"]) <= 5
    assert body["count"] == len(body["hits"])
    assert body["took_ms"] >= 0

    assert client.get("/api/v1/knowledge/search?q=x", headers=H).status_code == 422
    assert client.get("/api/v1/knowledge/search?q=ok&source=bogus", headers=H).status_code == 422
    assert client.get("/api/v1/knowledge/search?q=ok&limit=99", headers=H).status_code == 422


def test_api_files_list(app):
    client = login(app)
    resp = client.get("/api/v1/knowledge/files", headers=H)
    assert resp.status_code == 200, resp.text
    files = resp.json()["files"]
    assert len(files) >= 15
    sources = {f["source"] for f in files}
    assert sources == {"knowledge", "docs"}
    for entry in files:
        assert entry["file"].endswith(".md")
        assert entry["sections"] >= 1

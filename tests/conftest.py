"""Chia sẻ state giữa các test module.

Rate-limit của auth/public là dict in-memory cấp module — nếu không dọn, các test
sau sẽ "thừa" lỗi đăng nhập của test trước (đặc biệt bucket IP thuần dùng chung
IP giả lập "testclient").
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pytest  # noqa: E402

from backend.api.routers import auth as auth_router  # noqa: E402
from backend.api.routers import public as public_router  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_rate_limit_buckets():
    auth_router._FAILURES.clear()
    public_router._HITS.clear()
    yield
    auth_router._FAILURES.clear()
    public_router._HITS.clear()

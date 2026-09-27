"""Wiring engine vào báo cáo: PHS→Health, mốc chu kỳ→Purpose, transit→Practical."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend.reporting.contract import ReportRequest
from backend.reporting.orchestrator import ReportOrchestrator

SUBJECT = {
    "name": "Khách hàng thử nghiệm",
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "birth_location": "Hòa Bình, Việt Nam",
}


def _section_markdown(section_ids=("health", "purpose"), tier="deep_core"):
    doc = ReportOrchestrator().run(
        ReportRequest.model_validate({"subject": SUBJECT, "tier": tier, "domains": list(section_ids)}))
    return doc, {s.id: s.content_markdown for s in doc.sections}


def test_health_report_carries_phs_variables():
    doc, md = _section_markdown(("health",))
    assert "PHS & 4 MŨI TÊN" in md["domain_health"]
    assert doc.chart["variables"]["code"] in md["domain_health"]


def test_purpose_report_carries_cycle_milestones():
    _, md = _section_markdown(("purpose",))
    assert "MỐC CHU KỲ LỚN" in md["domain_purpose"]
    assert "Saturn Return" in md["domain_purpose"] or "Solar Return" in md["domain_purpose"]


def test_practical_actions_carries_today_transit():
    doc = ReportOrchestrator().run(
        ReportRequest.model_validate({"subject": SUBJECT, "tier": "deep_core"}))
    practical = next(s for s in doc.sections if s.id == "practical_actions")
    assert "Transit hôm nay" in practical.content_markdown
    assert practical.data["transit_today"]["undefined_hits"] is not None


def test_gene_keys_file_lists_all_64():
    import re
    text = (pathlib.Path(__file__).resolve().parents[1] / "knowledge" / "27_gene_keys_64_chi_tiet.md").read_text(encoding="utf-8")
    keys = sorted(int(k) for k in re.findall(r"\*\*Key (\d+)\*\*", text))
    assert keys == list(range(1, 65))
    assert "**Key 1** — Shadow Entropy" in text
    assert "Victimisation (nạn nhân)" in text

"""Runtime smoke tests for the current v3.0 contract."""

import ast
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "mcp"))

from hd_calculator import calculate_hd_chart  # noqa: E402


def _decorator_counts(path: pathlib.Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    counts = {"tools": 0, "resources": 0, "prompts": 0, "routes": 0}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            source = ast.unparse(decorator)
            if "mcp.tool" in source:
                counts["tools"] += 1
            if "mcp.resource" in source:
                counts["resources"] += 1
            if "mcp.prompt" in source:
                counts["prompts"] += 1
            if path.name == "openapi_server.py" and source.startswith("app."):
                counts["routes"] += 1
    return counts


def test_chart_calculation_smoke():
    chart = calculate_hd_chart(__import__("datetime").datetime(1990, 5, 15, 1, 30))
    assert chart["type"] in {"Generator", "Manifesting Generator", "Projector", "Manifestor", "Reflector"}
    assert chart["authority"]
    assert chart["profile"]
    assert len(chart["defined_centers"]) <= 9
    assert len(chart["all_activated_gates"]) > 0


def test_source_and_manifest_counts_match():
    server_counts = _decorator_counts(ROOT / "mcp" / "server.py")
    openapi_counts = _decorator_counts(ROOT / "mcp" / "openapi_server.py")
    manifest = json.loads((ROOT / "mcp" / "tools_manifest_latest.json").read_text(encoding="utf-8"))

    assert server_counts == {"tools": 36, "resources": 22, "prompts": 0, "routes": 0}
    assert openapi_counts["routes"] == 38
    assert len(manifest["tools"]) == server_counts["tools"]
    assert len(manifest["resources"]) == server_counts["resources"]
    assert manifest["prompts"] == []
    tool_names = {tool["name"] for tool in manifest["tools"]}
    resource_uris = {resource["uri"] for resource in manifest["resources"]}
    assert {"explain_calculation_method", "analyze_centers_deep", "analyze_channels_deep", "analyze_type_strategy_authority", "analyze_profile_definition", "analyze_practical_application"} <= tool_names
    assert {"human-design://knowledge/calculation", "human-design://knowledge/applications", "human-design://knowledge/channels"} <= resource_uris
    skill_files = sorted(path.name for path in (ROOT / "mcp" / "skills").glob("*.md"))
    assert manifest["skill_count"] == 25
    assert manifest["skills"] == skill_files


def test_openapi_app_imports():
    import openapi_server

    paths = {route.path for route in openapi_server.app.routes}
    assert "/health" in paths
    assert "/calculate-chart" in paths
    assert "/generate-team-report" in paths

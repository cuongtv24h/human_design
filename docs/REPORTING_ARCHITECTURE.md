# Report Contract và Report Orchestrator

Tài liệu này mô tả application layer dành cho Admin/Coach. Frontend, billing và payment chưa thuộc scope của layer này.

## Mục tiêu

Report layer biến một yêu cầu của Admin thành một report document có thể lưu, preview và render lại mà không cần tính chart lần nữa:

```text
Customer input
  ↓
ChartSnapshot
  ↓
ReportPlan
  ↓
Tool/domain analyzers
  ↓
Normalized ReportSection[]
  ↓
ReportDocument
  ↓
Markdown/HTML/PDF renderer
```

`backend/reporting/contract.py` là schema chuẩn. `backend/reporting/orchestrator.py` là entry point điều phối. `backend/reporting/catalog.py` là product catalog của tier và domain.

## Contract chính

- `SubjectInput`: ngày, giờ, timezone và thông tin định danh của khách hàng.
- `PartnerInput`: dữ liệu đối tác cho relationship/composite report.
- `ReportRequest`: tier, domain add-on, output format, locale và options.
- `ReportTier`: `free_basic` hoặc `deep_core`.
- `DomainName`: `money`, `potential`, `health`, `relationship`, `decision`, `deconditioning`, `purpose`, `team`.
- `ReportPlan`: definition, thứ tự section, tool và knowledge dependencies.
- `ReportSection`: dữ liệu có cấu trúc, Markdown tùy chọn, trạng thái, source tools và knowledge references.
- `ReportProvenance`: version của orchestrator/calculator/knowledge và thời điểm tạo.
- `ReportDocument`: chart snapshot, input snapshot, plan, sections, warning và provenance.

Raw chart và raw analyzer output luôn nằm trong `chart` hoặc `ReportSection.data`. `content_markdown` là lớp trình bày deterministic hiện tại; một LLM sau này chỉ được biên tập/diễn giải output có cấu trúc này, không được tính lại chart.

## Tier và domain

Tier và domain là hai chiều độc lập:

| Tier | Core sections |
| --- | --- |
| `free_basic` | summary, Type/Strategy/Authority, Profile/Definition, Centers, Practical actions |
| `deep_core` | toàn bộ Free Basic + Channels/Gates + Incarnation Cross |

Domain được thêm vào cùng một orchestrator, ví dụ:

- `deep_core + money`
- `deep_core + relationship + decision`
- `free_basic + health`

Không tạo codepath riêng cho từng combination. Catalog bổ sung section và adapter theo `DomainName`.

## Admin/Coach usage

```python
from backend.reporting.contract import ReportRequest
from backend.reporting.orchestrator import ReportOrchestrator

request = ReportRequest.model_validate({
    "subject": {
        "name": "Nguyễn Văn A",
        "birth_date": "1990-05-15",
        "birth_time": "08:30",
        "timezone": "+07:00",
        "birth_location": "Hòa Bình, Việt Nam",
    },
    "tier": "deep_core",
    "domains": ["money", "decision"],
    "requested_by": "coach-001",
})

document = ReportOrchestrator().generate(request)
preview_markdown = document.to_markdown()
```

Đối với relationship, thêm `partner` vào request. `document.model_dump_json()` là payload phù hợp để lưu snapshot hoặc đưa sang renderer/API sau này.

## Adapter policy

Orchestrator tính chart đúng một lần bằng `tools/hd_calculator.py`. Các domain adapter gọi trực tiếp analyzer và formatter hiện có trong `tools/`:

| Domain | Analyzer | Formatter |
| --- | --- | --- |
| Money | `analyze_money_map` | `format_money_report` |
| Potential | `analyze_potential_blindspots` | `format_potential_report` |
| Health | `analyze_health` | `format_health_report` |
| Relationship | `analyze_relationship` | `format_relationship_report` |
| Decision | `analyze_decision` | `format_decision_report` |
| Deconditioning | `analyze_deconditioning` | `format_deconditioning_report` |
| Purpose | `analyze_purpose` | `format_purpose_report` |
| Team | `analyze_team` | `format_team_report` |

Nếu một domain lỗi, section được đánh dấu `failed` và warning được lưu trong document thay vì làm mất toàn bộ report. Lỗi chart input vẫn làm request thất bại vì không thể tạo report có provenance đúng.

## Reproducibility và giới hạn

- `chart` được giữ nguyên dưới dạng JSON-safe snapshot.
- `input_snapshot` giữ request đã chuẩn hóa.
- provenance giữ source tools, knowledge references và versions.
- Không có billing/payment hoặc frontend trong layer này.
- Không dùng LLM để tính gate, channel, center, type, authority hay profile.
- `health` là nội dung tự quan sát Human Design; không thay thế chẩn đoán y khoa.

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

`backend/reporting/contract.py` là schema chuẩn. `backend/reporting/orchestrator.py` là entry point điều phối. `backend/reporting/catalog.py` là product catalog của tier và domain. `tools/hd_language.py` là lớp thuật ngữ tiếng Việt chuẩn dùng chung cho mọi nơi hiển thị. `backend/reporting/llm_editor.py` là lớp biên tập LLM. `backend/reporting/export.py` xuất file cuối (Markdown + BodyGraph SVG).

## Chuẩn cấu trúc báo cáo

Mọi báo cáo gồm ba khối, đúng thứ tự:

1. **Thông tin người được phân tích** — tên, ngày/giờ sinh, múi giờ, nơi sinh
   (và đối tác nếu có) — render tự động ở đầu `to_markdown()`.
2. **Bản đồ BodyGraph tự sinh** qua công cụ (`tools/hd_bodygraph.py`) —
   `export_report(document, out_dir)` viết `<slug>_bodygraph.svg` và nhúng
   `![BodyGraph](...)` vào Markdown.
3. **Nội dung** theo một trong hai `content_mode`:

| content_mode | Ai viết nội dung | Cách vận hành |
| --- | --- | --- |
| `template` (mặc định) | Renderer deterministic | `orchestrator.run()` ra Markdown cuối cùng |
| `llm` | LLM biên tập trên dữ liệu nguồn | `build_llm_brief(document)` → LLM → `merge_llm_draft(document, drafts)` |

### Chế độ LLM (content_mode = "llm")

LLM đóng vai **nhà chuyên môn bộ môn + chuyên gia tư vấn, tâm lý**; viết thấu
cảm và tâm tình dẫn dắt. Pipeline trong repo là deterministic — repo không gọi
LLM:

```text
ReportDocument (template)
  → build_llm_brief(document)      # persona + quy tắc + dữ liệu nguồn JSON
                                    # + cấu trúc/template tham chiếu + bảng thuật ngữ chuẩn
  → LLM bên ngoài biên tập, trả về {"<section_id>": "<markdown mới>"}
  → merge_llm_draft(document, drafts, editor_model)
      ├─ validate_llm_draft(): giữ nguyên sự kiện kỹ thuật (Type, Strategy,
      │   Authority, Profile, Definition, Cross...) — thiếu → cảnh báo
      └─ provenance.editor = "llm:<model>"
```

Quy tắc cứng (trong `LLM_RULES`): không tính lại, không bịa số, thuật ngữ
song ngữ trau chuốt theo `tools/hd_language.py`, tỉ lệ 70/30, giữ tiêu đề/thứ
tự phần. Dữ liệu thô trong `chart`/`ReportSection.data` không bao giờ bị thay
bởi LLM.

## Contract chính

- `SubjectInput`: ngày, giờ, timezone và thông tin định danh của khách hàng.
- `PartnerInput`: dữ liệu đối tác cho relationship/composite report.
- `ReportRequest`: tier, template, domain add-on, output format, locale và options.
- `ReportTemplate`: `sections` (mặc định, structured theo tier) hoặc `operating_manual` (narrative 5 phần chuẩn).
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
| `deep_core` | toàn bộ Free Basic + Channels/Gates (tên kênh song ngữ + câu đời sống + cổng treo kèm ý nghĩa) + Incarnation Cross (khung diễn giải + 4 cổng + Quarters) |

Domain được thêm vào cùng một orchestrator, ví dụ:

- `deep_core + money`
- `deep_core + relationship + decision`
- `free_basic + health`

Không tạo codepath riêng cho từng combination. Catalog bổ sung section và adapter theo `DomainName`.

## Report template

Template là chiều thứ ba, độc lập với tier và domain: tier chọn *bao nhiêu* dữ liệu
chart được phân tích, template chọn *cách viết*.

| Template | Section chuẩn | Phong cách |
| --- | --- | --- |
| `sections` (mặc định) | 5 section structured theo tier (`summary` ... `practical_actions`) | Dữ liệu kỹ thuật kèm phân tích ngắn, thuật ngữ song ngữ tùy biến |
| `operating_manual` | 5 phần tự sự (`part1_identity` ... `part5_field_application`) | "Cẩm nang vận hành" bằng tiếng Việt đời sống, chuẩn `docs/NARRATIVE_STANDARD.md` |

Template `operating_manual` render qua `backend/reporting/narrative.py` trên lớp ngôn
ngữ `backend/reporting/language_vn.py` + `tools/hd_language.py`; deterministic, không
LLM. Thuật ngữ chuẩn (Type, Strategy, Authority, Definition, Centers, Signature/Not-Self)
lấy từ `tools/hd_language.py` — cùng bộ từ dùng cho mọi nơi hiển thị. Domain add-on vẫn
được gắn sau 5 phần chuẩn trong cùng `ReportDocument`.

```python
request = ReportRequest.model_validate({
    "subject": { ... },
    "template": "operating_manual",   # mặc định: "sections"
})
```

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

**Ngôn ngữ hiển thị:** mọi Markdown hiển thị (cả hai template và cả 8 formatter domain,
cộng `hd_analyzer`/`hd_report_pdf`) render thuật ngữ qua lớp chuẩn
`tools/hd_language.py` — không chuỗi song ngữ thô của calculator. `ReportSection.data`
và `chart` snapshot vẫn giữ giá trị thô làm source of truth.

Nếu một domain lỗi, section được đánh dấu `failed` và warning được lưu trong document thay vì làm mất toàn bộ report. Lỗi chart input vẫn làm request thất bại vì không thể tạo report có provenance đúng.

## Reproducibility và giới hạn

- `chart` được giữ nguyên dưới dạng JSON-safe snapshot.
- `input_snapshot` giữ request đã chuẩn hóa.
- provenance giữ source tools, knowledge references và versions.
- Không có billing/payment hoặc frontend trong layer này.
- Không dùng LLM để tính gate, channel, center, type, authority hay profile.
- `health` là nội dung tự quan sát Human Design; không thay thế chẩn đoán y khoa.

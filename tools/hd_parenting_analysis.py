#!/usr/bin/env python3
"""
Human Design Parenting Analysis - Nuôi dạy con theo thiết kế (v1.0)
Nhu cầu thực tế: cha mẹ hiểu con thuộc Type/Profile/Authority nào để nuôi
đúng cách thay vì ép con thành khuôn mẫu chung.
Child Type deep dive (mô tả + vết thương + 7 lời khuyên) + Profile con +
Authority con + Centers con + lộ trình 7 ngày / 7 tháng / 7 năm.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart
from hd_language import vn_type

CHILD_TYPE = {
    "Generator": {
        "desc": "Năng lượng dồi dào khi được làm điều mình thích. Con cần được HỎI (câu hỏi có/không) để Sacral hồi đáp, không phải bị đẩy đi.",
        "wound": "Bị ép học/làm việc không yêu thích -> Frustration sớm, kiệt sức Sacral, mất niềm tin vào cảm nhận cơ thể.",
        "not_type": "đừng ép con thành người khởi xướng mọi thứ - hãy để con hồi đáp",
        "advice": [
            "Hỏi con câu hỏi có/không: 'Con có muốn... không?' để con kết nối uh-huh (đồng ý) / uh-uh (từ chối).",
            "Đừng ép con khởi xướng - hãy bày việc ra và quan sát con bị hút về phía nào.",
            "Cho con thử nhiều việc để tìm ra điều yêu thích; đổi hướng giữa chừng là thăm dò, không phải thiếu tập trung.",
            "Tôn trọng khi con nói uh-uh (không) - đó là con đang bảo vệ năng lượng của mình.",
            "Dạy con lắng nghe bụng thay vì đầu óc: 'Bụng con thấy ừ hay hừ?'",
            "Đừng ép hoàn thành cho bằng được - cho phép con quay lại dự án cũ một cách tự nhiên.",
            "Cha mẹ làm gương lắng nghe phản ứng cơ thể của chính mình - con học bằng ví dụ.",
        ],
    },
    "Manifesting Generator": {
        "desc": "Nhanh, đa nhiệm, thích thử nhiều thứ cùng lúc và tìm đường tắt. Con vẫn cần chốt Sacral có/không rồi mới thả tốc độ.",
        "wound": "Bị ép làm 1 việc, làm chậm lại, làm theo từng bước -> Frustration + Anger, cảm thấy mình 'có vấn đề'.",
        "not_type": "đừng ép con thành người làm từng bước một - hãy thả tốc độ sau khi chốt hướng",
        "advice": [
            "Hỏi có/không để chốt hướng trước, rồi thả cho con chạy nhanh theo cách của con.",
            "Cho con thử nhiều việc cùng lúc - đa luồng là thiết kế tối ưu của con.",
            "Cho phép con bỏ qua bước nếu con thấy hiệu quả hơn - đừng bắt làm đúng quy trình.",
            "Dạy con thông báo khi đổi ý: 'Con làm cách khác nhé' để bớt bị hiểu lầm là bướng.",
            "Đừng ép con cam kết 1 việc cả đời từ sớm - con cần không gian bẻ lái.",
            "Khi con kẹt + cáu: cho quyền chọn lại thay vì ép tiếp tục.",
            "Khen tốc độ và hiệu quả của con, không chê con 'ẩu' vì làm tắt.",
        ],
    },
    "Projector": {
        "desc": "Nhạy cảm, nhìn thấy người khác và hệ thống. Con cần được CÔNG NHẬN và MỜI, không phải bị ép làm nhiều như Generator.",
        "wound": "Bị ép làm việc nhiều, không được công nhận, bị bỏ qua -> Cay đắng sớm, kiệt sức, cảm thấy vô hình.",
        "not_type": "đừng ép con thành người làm 8 tiếng như Generator - hãy mời và công nhận",
        "advice": [
            "Công nhận cụ thể: 'Mẹ thấy con giỏi X / để ý được Y' thay vì khen chung chung.",
            "Mời con tham gia: 'Con có muốn... không?' - lời mời đúng xây lòng tự trọng.",
            "Cho con nghỉ ngơi nhiều, ngủ một mình - năng lượng con có hạn và cần nạp lại.",
            "Đừng ép con đua tranh hay chạy theo nhịp bạn bè - quý chất lượng hơn số lượng.",
            "Hỏi ý kiến con về hệ thống/lớp học - con nhìn thấy điều người khác không thấy.",
            "Dạy con chờ lời mời thay vì ép lời khuyên lên người khác.",
            "Tạo môi trường nơi góc nhìn của con được lắng nghe - ở đó con tự tin bung nở.",
        ],
    },
    "Manifestor": {
        "desc": "Bẩm sinh biết mình muốn làm gì và khi nào cần làm. Con cần TỰ CHỦ trong khuôn khổ an toàn + học cách THÔNG BÁO.",
        "wound": "Cha mẹ/giáo viên áp đặt rào cản vì lo con tự ý -> hình phạt tâm lý -> phản ứng mạnh mẽ hoặc lén lút khi lớn.",
        "not_type": "đừng ép con thành đứa trẻ răm rắp nghe lời - hãy dạy con thông báo",
        "advice": [
            "Dạy con thông báo thay vì xin phép: 'Con sẽ làm...' - một câu báo giảm phần lớn xung đột.",
            "Đừng kiểm soát chi tiết - giao mục tiêu/khung an toàn, để con tự chọn cách làm.",
            "Tôn trọng độc lập của con: đừng bảo con phải làm gì từng ly từng tí.",
            "Cho con không gian riêng và thời gian một mình - hào quang khép kín cần nạp lại.",
            "Đừng trừng phạt khi con tự ý - hỏi 'Con đã thông báo chưa?' rồi dạy lại bước đó.",
            "Khen mỗi khi con chủ động thông báo - củng cố thói quen thay thế xin phép.",
            "Hiểu con không có năng lượng bền như Generator - tôn trọng nhịp bùng rồi nghỉ.",
        ],
    },
    "Reflector": {
        "desc": "Cực kỳ nhạy cảm với môi trường như bọt biển hút năng lượng xung quanh. Môi trường là TẤT CẢ với con.",
        "wound": "Ở môi trường không đúng, với người không đúng -> Thất vọng sớm, lạc lõng, cảm thấy không thuộc về đâu.",
        "not_type": "đừng ép con thành người quyết nhanh hòa nhập nhanh - hãy cho môi trường lành và thời gian",
        "advice": [
            "Ưu tiên môi trường: không gian thiên nhiên, nơi an toàn, nhịp sinh hoạt ổn định.",
            "Đừng ép con quyết định nhanh - quyết định lớn cho con thời gian (tới 28 ngày).",
            "Nếu con thất vọng/rối loạn: kiểm tra môi trường trước khi sửa đứa trẻ.",
            "Cho con ngủ một mình, không gian riêng để 'xả' năng lượng vay mượn trong ngày.",
            "Công nhận sự nhạy cảm: 'Ừ, mẹ cũng thấy...' thay vì gạt đi là tưởng tượng.",
            "Khuyến khích con diễn đạt điều quan sát được: kể chuyện, vẽ, viết nhật ký.",
            "Kiên nhẫn với nhịp chậm của con - chậm là cơ chế xử lý, không phải chậm hiểu.",
        ],
    },
}

PROFILE_CHILD = {
    "1/3": "Cần nền tảng vững chắc + được thử sai. Cho con học kỹ rồi thả ra trải nghiệm, đừng phạt vấp ngã đầu đời.",
    "1/4": "Cần nền tảng + vòng bạn thân ổn định. Đừng đổi trường/lớp liên tục khi con chưa sẵn sàng.",
    "2/4": "Tài năng tự nhiên cần ở một mình rồi được gọi ra. Đừng lôi con ra sân khấu sai lúc.",
    "2/5": "Tài năng ẩn + dễ bị kỳ vọng. Bảo vệ con khỏi áp lực 'con phải cứu cả lớp'.",
    "3/5": "Thử sai va chạm lớn. Chuẩn bị tâm lý: con sẽ ngã nhiều - việc của cha mẹ là đệm đỡ, không phải rào cấm.",
    "3/6": "Ba giai đoạn đời. Tuổi nhỏ cứ để con thử - càng về sau con càng thành hình mẫu.",
    "4/1": "Hiếm (2%), định mệnh cố định một đường. Tôn trọng sự cứng đầu đúng thiết kế của con.",
    "4/6": "Cần bạn bè gắn bó lâu dài. Nuôi dưỡng các mối quan hệ thân thiết của con.",
    "5/1": "Bị kỳ vọng lớn từ sớm. Dạy con quyền nói 'việc này con không làm được' để không gãy.",
    "5/2": "Vừa bị gọi tên vừa cần hang riêng. Cân bằng giúp con: việc chung + thời gian một mình.",
    "6/2": "Ba giai đoạn + ẩn sĩ. Tuổi nhỏ cho thử, tuổi teen tôn trọng khoảng rút lui quan sát.",
    "6/3": "Hình mẫu qua thử sai liên tục. Con học bằng trải nghiệm cả đời - đừng ép con 'nghe lời là xong'.",
}

AUTHORITY_CHILD = {
    "emotional": "Thẩm quyền Cảm xúc: dạy con KHÔNG quyết ngay lúc cao trào. Cho con ngủ một đêm (vài ngày với việc lớn) rồi hỏi lại.",
    "sacral": "Thẩm quyền Sacral: dạy con nghe âm uh-huh/uh-uh. Hỏi có/không, đừng hỏi 'tại sao' - con quyết bằng bụng.",
    "splenic": "Thẩm quyền Lá lách: trực giác tức thì, nói một lần rồi thôi. Dạy con tin vào cảm nhận đầu tiên về an toàn/nguy hiểm.",
    "ego": "Thẩm quyền Ego/Ý chí: con cần được nói 'con muốn'. Tôn trọng ý chí của con, đừng ép con hy sinh mong muốn để vừa lòng.",
    "self": "Thẩm quyền Self-Projected: con cần NÓI RA để nghe rõ mình. Lắng nghe con nói hết, đừng cắt ngang hay quyết hộ.",
    "mental": "Thẩm quyền Môi trường/Tinh thần: con cần đúng không gian + nói với nhiều người để rõ dần. Đừng ép con quyết một mình trong phòng kín.",
    "lunar": "Thẩm quyền Mặt trăng: quyết định lớn cần đủ 28 ngày. Dạy con theo dõi mình qua một chu kỳ rồi mới chốt.",
    "none": "Không có thẩm quyền nội tại rõ ràng: quay về Loại và Chiến lược của con - đó là la bàn chính.",
}


def _authority_key(authority: str) -> str:
    a = (authority or "").lower()
    for key in ("emotional", "sacral", "splenic", "ego", "self", "mental", "lunar"):
        if key in a:
            return key
    return "none"


def analyze_parenting(birth_datetime, name=""):
    # Accept a precomputed chart when called from the report pipeline.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t, p = chart["type"], chart["profile"]
    child = CHILD_TYPE[t]
    defined = set(chart["defined_centers"])
    all_centers = {"Head", "Ajna", "Throat", "G", "Heart", "Solar Plexus", "Sacral", "Spleen", "Root"}
    open_centers = sorted(all_centers - defined)
    authority = chart.get("authority", "")
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": p, "authority": authority,
        "definition": chart.get("definition", ""),
        "defined_centers": sorted(defined),
        "parenting_analysis": {
            "child_type": {"type": t, "desc": child["desc"], "wound": child["wound"],
                           "not_type": child["not_type"], "advice": child["advice"]},
            "profile_child": {"profile": p, "guidance": PROFILE_CHILD.get(p, "")},
            "authority_child": {"authority": authority,
                                "guidance": AUTHORITY_CHILD[_authority_key(authority)]},
            "open_centers": open_centers,
            "centers_note": ("Các trung tâm mở là nơi con học trí tuệ qua tiếp xúc - cũng là nơi con dễ bị "
                             "điều kiện hóa nhất. Quan sát con ở những nơi này thay vì ép con 'mạnh mẽ lên'."),
            "roadmap": [
                "7 ngày: thử 1 thay đổi duy nhất (cách hỏi con / cách giao việc / giờ nghỉ).",
                "7 tháng: quan sát tín hiệu lệch thiết kế giảm dần (bớt cáu, bớt thu mình, ngủ ngon hơn).",
                "7 năm: đồng hành deconditioning cùng con - cha mẹ sống đúng thiết kế của mình trước.",
            ],
            "summary": (f"{name or 'Con'} ({t} {p}, {authority}): {child['desc']} "
                        f"Nguyên tắc nhớ: {child['not_type']}."),
        },
        "áp_dụng_cho": "100% cha mẹ - Nuôi dạy con theo Type/Profile/Authority",
    }


def format_parenting_report(d):
    r = d["parenting_analysis"]
    c = r["child_type"]
    L = [f"# BÁO CÁO NUÔI DẠY CON - {d['name']} - {d['type']} {d['profile']}",
         f"**Loại năng lượng:** {vn_type(d['type'], gloss=True)} | **Hồ sơ:** {d['profile']} | **Thẩm quyền:** {d['authority']}",
         "", "## 1. TỔNG QUAN CON", r["summary"],
         "", f"## 2. CON THUỘC TYPE {d['type'].upper()} - NUÔI SAO CHO ĐÚNG",
         f"**Bản chất:** {c['desc']}", "",
         f"**Vết thương cần tránh:** {c['wound']}", "",
         "**7 lời khuyên cho cha mẹ:**"]
    L += [f"{i + 1}. {a}" for i, a in enumerate(c["advice"])]
    L += ["", f"## 3. PROFILE {r['profile_child']['profile']} Ở TRẺ EM",
          r["profile_child"]["guidance"],
          "", "## 4. DẠY CON RA QUYẾT ĐỊNH THEO THẨM QUYỀN",
          f"**{r['authority_child']['authority']}:** {r['authority_child']['guidance']}",
          "", "## 5. TRUNG TÂM MỞ CỦA CON - NƠI CON HỌC TRÍ TUỆ",
          f"**Trung tâm mở:** {', '.join(r['open_centers']) if r['open_centers'] else 'Không có (hiếm)'}",
          r["centers_note"],
          "", "## 6. LỘ TRÌNH ĐỒNG HÀNH"]
    L += [f"- {s}" for s in r["roadmap"]]
    L += ["", "## 7. KẾT LUẬN",
          f"{c['not_type'].capitalize()}.",
          "> \"Nuôi con không phải nặn con thành điều mình muốn - mà là dẫn dắt con người con vốn là\""]
    return "\n".join(L)

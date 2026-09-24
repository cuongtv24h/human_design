"""Lớp ngôn ngữ tiếng Việt TỰ NHIÊN cho Human Design.

Đây là "từ điển sống" của báo cáo: mỗi thuật ngữ kỹ thuật (Type, Strategy,
Authority, Center, Profile, Definition, Cross) đều có một cách diễn đạt bằng
ngôn ngữ đời sống — theo chuẩn trong ``docs/NARRATIVE_STANDARD.md``.

Nguyên tắc:
- Renderer báo cáo LUÔN dẫn ngôn ngữ đời sống trước; thuật ngữ kỹ thuật chỉ
  xuất hiện ở dòng "Thuật ngữ:" cuối phần (tỷ lệ 70/30).
- Không bao giờ in chuỗi thô kiểu "Wait to Respond - Chờ để Đáp Ứng".
- Thuật ngữ chuẩn hiển thị ở MỌI nơi (dòng Thuật ngữ, BodyGraph, MCP...) lấy
  từ lớp dùng chung ``tools/hd_language.py`` (``hd_language``); file này chỉ
  thêm phần kể chuyện đời sống bên trên các thuật ngữ đó.
- Nội dung ở đây là dữ liệu (không phải logic tính toán): chart vẫn do
  ``tools/hd_calculator.py`` sinh ra; lớp này chỉ phụ trách cách kể.
"""

from __future__ import annotations

import sys
from pathlib import Path

_TOOLS_DIR = str(Path(__file__).resolve().parents[2] / "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# Lớp thuật ngữ chuẩn dùng chung (mọi nơi hiển thị).
from hd_language import (  # noqa: E402
    AUTHORITY_VN,
    CENTER_VN,
    DEFINITION_VN,
    NOT_SELF_SIGNATURE,
    STRATEGY_VN,
    TYPE_VN,
    UI,
    vn_authority,
    vn_center,
    vn_definition,
    vn_strategy,
    vn_type,
)

__all__ = [
    "AUTHORITY_VN",
    "CENTER_VN",
    "DEFINITION_VN",
    "NOT_SELF_SIGNATURE",
    "STRATEGY_VN",
    "TYPE_VN",
    "UI",
    "vn_authority",
    "vn_center",
    "vn_definition",
    "vn_strategy",
    "vn_type",
]

# ---------------------------------------------------------------------------
# TYPE (5) — Phần 1: "Bạn thực sự là ai?"
# ---------------------------------------------------------------------------

TYPE_LANGUAGE: dict[str, dict[str, str]] = {
    "Generator": {
        "life_name": "Người kiến tạo bền bỉ",
        "population": "khoảng 37% dân số",
        "car": "một chiếc xe đường trường có thùng nhiên liệu gần như vô tận — không sinh ra để sprint, mà để đi dài hơi và đi thật xa.",
        "aura": "Bạn có một 'cửa năng lượng' luôn mở ở vùng thượng vị: cuộc đời liên tục gửi việc đến, và bạn mang sẵn nguồn lực bên trong để đáp ứng mà không cạn kiệt. Bạn không cần ai châm ngòi — chỉ cần việc gọi, và bạn 'ừ ừ'.",
        "strategy_life": "Hãy để cơ hội tự tìm đến bạn, thay vì bạn rượt đuổi. Khi có việc gõ cửa và vùng thượng vị phát ra tiếng 'ừ ừ' (uh-huh) thật — không phải tiếng ừ vì lịch sự — đó là lúc dồn năng lượng. Rượt đuổi việc không gọi là chạy sai nhiên liệu.",
        "signature_life": "Thoả mãn — cảm giác ấm và gọn kiểu 'à, đúng rồi', xuất hiện khi bạn sống đúng nhịp.",
        "not_self_life": "Kiệt sức, bực dọc (frustration) — tín hiệu bạn đang làm việc không được gọi, hoặc chạy theo nhịp của người khác.",
        "work_fit": "Bạn tỏa sáng ở môi trường có dòng việc liên tục và cho bạn quyền tự chủ cách làm. Vai trò 'làm một cú rồi xong' sẽ làm bạn khô; việc đều đặn, lặp lại được mà vẫn thấy tiến bộ mới là nguồn nuôi bạn.",
        "energy_protection": "Mỗi ngày, giữ một khung giờ chỉ thuộc về bạn — không họp, không tin nhắn, không 'giúp vội' — để thùng nhiên liệu được nạp lại từ chính bạn.",
        "relationship_hint": "Bạn thể hiện tình yêu an toàn nhất qua việc 'làm cùng': một mục tiêu chung bền vững, xây bên nhau, là cách bạn gần nhau mà không làm mất năng lượng.",
    },
    "Manifesting Generator": {
        "life_name": "Người kiến tạo nhiều hướng",
        "population": "khoảng 33% dân số",
        "car": "một chiếc xe đường trường có thùng nhiên liệu vô tận, kèm hộp số tự do — bạn có thể và nên đổi hướng giữa chừng, chỉ cần thông báo cho người ngồi cùng xe.",
        "aura": "Bạn vừa có 'cửa năng lượng' mở như Generator, vừa có ý chí (Heart) để tự khởi động. Cuộc đời gửi việc đến cho bạn, và bạn không cần chờ ai đồng ý để chuyển hướng — đó là thiết kế, không phải bướng bỉnh.",
        "strategy_life": "Chờ cuộc đời gọi trước, rồi đáp ứng — và thông báo khi bạn đổi hướng hoặc dừng lại. Bạn không cần xin phép để chuyển sang việc mới, nhưng người làm việc cùng bạn có quyền biết, để họ không bị 'văng ra khỏi đường ray'.",
        "signature_life": "Thoả mãn — cảm giác trọn vẹn khi mọi thứ bạn bắt tay vào đều 'ra được kết quả thật'.",
        "not_self_life": "Kiệt sức, bực dọc (frustration); và khi bị ép phải chọn đúng một lối duy nhất — giận (anger). Dấu hiệu: bạn tự hỏi 'mình đang cố giữ cam kết này cho ai?'.",
        "work_fit": "Bạn phù hợp với môi trường đa dự án, nhịp nhanh, cho phép đổi hướng. Vai trò gò bạn vào 'một kế hoạch bất biến' sẽ làm bạn nghẹt; nơi tôn trọng cả khởi xướng lẫn phản hồi mới nuôi được bạn.",
        "energy_protection": "Trước mỗi lần chuyển hướng, dành 30 giây 'thông báo' — cho người khác và cho chính mình: 'mình đang bỏ việc A để làm B, và đó là chủ ý'. Chuyển hướng có thông báo không tốn năng lượng; im lặng rồi chợt biến mất mới tốn.",
        "relationship_hint": "Người thân của bạn cần 'hợp đồng năng lượng' rõ: họ cần biết khi nào bạn có mặt trọn, khi nào bạn phải rút đi làm việc mới. Rõ từ đầu, tình cảm đi được dài hơn.",
    },
    "Projector": {
        "life_name": "Người dẫn đường sâu sắc",
        "population": "khoảng 20% dân số",
        "car": "một chiếc xe sang êm ái, nội thất thông minh nhưng thùng nhiên liệu nhỏ: không sinh ra để chạy đường dài liên tục, mà để đi những quãng đường đúng lúc, đúng người mời — và đi đúng lúc nào cũng tới đích.",
        "aura": "Bạn không có 'cửa năng lượng' mở liên tục như Generator — và đó không phải khuyết điểm. Năng lượng của bạn được thiết kế để dồn vào những khoảnh khắc quan trọng: lời khuyên, quyết định, dẫn dắt. Làm việc liên tục mỗi ngày là dùng sai thiết kế của chính mình.",
        "strategy_life": "Chờ lời mời. Bạn không cần 'ứng tuyển' vào cuộc đời — khi đúng người cần đúng thứ bạn có, họ sẽ mời. Làm việc chưa được mời (đặc biệt ở nơi không coi trọng bạn) là cách nhanh nhất để bạn cay đắng.",
        "signature_life": "Thành công — cảm giác 'mình đã làm đúng, và nó thành thật sự', gọn và sạch.",
        "not_self_life": "Cay đắng (bitterness) — cảm giác bị bỏ rơi, bị đánh giá thấp, làm nhiều được ít. Nếu cảm giác này đậm, hãy dừng lại và kiểm tra: mình đang làm việc không được mời không?",
        "work_fit": "Bạn tỏa sáng ở vai trò dẫn dắt, cố vấn, 'người chỉ đường' — ít việc nhưng mỗi việc chạm đúng. Môi trường chạy bằng số lượng giờ sẽ bào mòn bạn; nơi trả cho tầm nhìn và chất lượng mới tôn trọng thiết kế của bạn.",
        "energy_protection": "Giữ các khoảng 'không làm việc' thật sòng phẳng. Năng lượng của bạn không hồi phục bằng cà phê thứ năm; nó hồi phục khi bạn cho phép mình nghỉ giữa các lần được mời.",
        "relationship_hint": "Trong quan hệ, bạn thể hiện qua chiều sâu chứ không qua tần suất. Hãy nói rõ nhịp của mình sớm: 'tôi cần im lặng một lúc — đó là cách tôi nạp năng lượng để còn ở đây cho bạn'.",
    },
    "Manifestor": {
        "life_name": "Người khởi xướng độc lập",
        "population": "chỉ khoảng 9% dân số",
        "car": "một chiếc xe đầu kéo mở đường: sinh ra để khởi động trước, đi trước và tự chọn tốc độ — không cần chờ ai bật đèn xanh.",
        "aura": "Bạn có khả năng khởi động mà không bị 'phanh' bởi ý kiến người khác — trong Human Design, đó là ý chí (will). Người ta hay nói bạn 'cứng đầu'; thực ra bạn chỉ đang vận hành đúng thiết kế: không có 'trạm chờ' nào giữa ý tưởng và hành động.",
        "strategy_life": "Bạn được phép bắt đầu trước — chỉ cần thông báo cho những người bị ảnh hưởng, trước hoặc ngay khi bạn khởi động. Thông báo không phải xin phép: bạn không cần ai gật đầu, họ chỉ cần kịp 'thay số' khi bạn chuyển hướng.",
        "signature_life": "Bình yên (peace) — cảm giác trôi, không va đập, mọi thứ ở đúng chỗ.",
        "not_self_life": "Giận (anger) — cảm giác bị chặn, bị phán xét, bị yêu cầu 'thôi đi'. Giận của bạn là la bàn: nó chỉ vào nơi ai đó đang cố đè nhịp của bạn.",
        "work_fit": "Bạn phù hợp với vai trò khởi xướng, mở thị trường, 'người đi đầu'. Môi trường cần bạn chờ phê duyệt năm cấp để làm một việc nhỏ sẽ làm bạn muốn đập bàn. Hãy tự hỏi: chỗ này có cho phép mình đi trước không?",
        "energy_protection": "Trước mỗi việc lớn, dành 5 phút 'thông báo' cho 2-3 người trực tiếp bị ảnh hưởng. Đây là cách bạn giữ bình yên cho mình và cho họ — và là bí mật duy nhất của Manifestor: thông báo đúng người, đúng lúc.",
        "relationship_hint": "Người thân cần biết: 'khi tôi nói mình đang làm gì, đó là thông báo, không phải câu hỏi'. Một câu như vậy sẽ gỡ được một nửa xung đột trong gia đình.",
    },
    "Reflector": {
        "life_name": "Nhà soi gương của cộng đồng",
        "population": "chỉ khoảng 1% dân số",
        "car": "một chiếc xe có màn hình soi gương siêu nhạy: xe không tự chọn đường, mà phản chiếu chính xác con đường nó đang chạy — và từ đó, cả đội biết mình đang đi ở đâu.",
        "aura": "Bạn không có 'trạm năng lượng' nào định hình cố định — nên bạn là chiếc gương của môi trường: ở đâu, với ai, bạn phản chiếu nhịp và chất lượng của không gian đó. Đây là tài sản quý nhất của cộng đồng — và cũng là lý do bạn cần nhiều thời gian hơn để biết 'mình là ai ở đây'.",
        "strategy_life": "Chờ một vòng trăng (khoảng 28-29 ngày) trước khi quyết định quan trọng: việc mới, quan hệ mới, chuyển chỗ ở. Hai tuần đầu ở đâu đó chỉ cho bạn 'bề mặt'; cả một vòng trăng mới cho bạn thấy 'chiều sâu' của nơi đó — và của chính bạn trong đó.",
        "signature_life": "Bất ngờ (surprise) — cảm giác 'thú vị quá, không ngờ đến thế' — dấu hiệu bạn đang để cuộc đời bất ngờ bạn, thay vì gò nó vào khung của mình.",
        "not_self_life": "Thất vọng (disappointment) — cảm giác cô đơn, lạc lõng, 'mình không hợp với đâu cả'. Nếu nó kéo dài, hãy kiểm tra: mình có đang ở sai môi trường, hoặc đang tự ép mình chạy theo nhịp người khác không?",
        "work_fit": "Bạn tỏa sáng ở vai trò 'tư vấn cuối cùng', người đánh giá chất lượng, nhà đầu tư dài hạn — những vị trí cần câu trả lời đúng, không cần câu trả lời nhanh. Tránh vai trò phải quyết liên tục mỗi ngày trong tuần đầu; đó là cách làm 'hư' chiếc gương.",
        "energy_protection": "Mỗi nơi mới, hãy dành đủ một vòng trăng 'chỉ quan sát'. Đừng tự đánh giá mình quá sớm: phản ứng của bạn trong hai tuần đầu không phải chân dung của bạn.",
        "relationship_hint": "Bạn là người phản chiếu — và người sống với bạn sẽ thấy thật của họ qua bạn. Hãy nhẹ nhàng với chính mình: việc 'hiểu mình' của bạn diễn ra theo chu kỳ trăng, không theo quý báo cáo.",
    },
}

# ---------------------------------------------------------------------------
# AUTHORITY (7) — Phần 2: "La bàn ra quyết định"
# ---------------------------------------------------------------------------


def resolve_authority(authority: str) -> str:
    """Map the raw calculator authority string to a language key."""
    a = (authority or "").lower()
    if "emotional" in a:
        return "emotional"
    if "sacral" in a:
        return "sacral"
    if "splenic" in a:
        return "splenic"
    if "self-projected" in a:
        return "self_projected"
    if "ego" in a or "heart" in a:
        return "ego"
    if "lunar" in a or "reflector" in a:
        return "lunar"
    return "mental"


AUTHORITY_LANGUAGE: dict[str, dict[str, object]] = {
    "emotional": {
        "compass_name": "Bộ la bàn sóng cảm xúc",
        "rule": "Cảm xúc của bạn chạy theo sóng: lúc đỉnh (vui, bực, sợ, phấn khích) la bàn lệch nhất; lúc mặt sóng phẳng, kim chỉ mới đúng. Quyết định quan trọng chỉ nên ra lúc phẳng.",
        "steps": [
            "Ghi lại câu hỏi ngay lúc nó xuất hiện — một dòng, không phân tích, không hỏi ai.",
            "Đợi sóng qua: chuyện nhỏ vài giờ, chuyện lớn đủ 48 tiếng.",
            "Quay lại đọc ở lúc phẳng nhất trong ngày: nếu câu trả lời vẫn đó, đó là câu trả lời thật của bạn.",
        ],
        "scenario_business": "Được mời hợp tác trong một buổi ăn tuyệt vời? Hãy nói: 'Mình để mang về, và sẽ trả lời sau 2-3 ngày.' Người đáng hợp tác sẽ còn đó; người chỉ muốn bạn chốt lúc nóng là người bạn nên tránh.",
        "scenario_purchase": "Muốn mua một thứ lớn: để nó vào 'giỏ chờ' 3-5 ngày. Ngày thứ hai, hỏi lại ở lúc tỉnh nhất: 'mình vẫn cần thật, hay chỉ đang mệt và muốn được chiều?'",
    },
    "sacral": {
        "compass_name": "Tiếng 'ừ ừ' của vùng thượng vị",
        "rule": "Cơ thể bạn trả lời câu hỏi có/không TRƯỚC khi não kịp lập luận. Tiếng 'ừ ừ' ấm ở vùng thượng vị là có; im lặng, hay phải nghĩ lâu, nghĩa là chưa phải lúc. Não chỉ việc báo cáo — không phải cơ quan quyết định.",
        "steps": [
            "Biến quyết định thành câu hỏi có/không: 'Mình nhận việc này không?' — không phải 'Mình nên cân nhắc thế nào?'",
            "Nghe phản hồi của vùng thượng vị trong 2-3 giây đầu, trước khi não kịp lên tiếng.",
            "Nếu không có 'ừ ừ' rõ — hoặc phải nghĩ rất lâu — thì coi như câu trả lời là 'chưa'. Đừng ép cơ thể trả lời thay não.",
        ],
        "scenario_business": "Lời mời hợp tác ập đến lúc bạn đang tập trung? Đừng 'ừ' vì lịch sự. Hãy nói thẳng: 'Để mình nghe bên trong một chút rồi trả lời ngay.' Một câu ấy giữ nguyên giá trị chữ ký của bạn.",
        "scenario_purchase": "Đứng trước món đồ ưng ý, hãy hỏi ngay: 'Mình mua không?' và nghe vùng thượng vị. 'Ừ ừ' ấm là mua không hối hận. Im lặng thì để lại — và 90% là bạn sẽ không quay lại mua, và đó là điều bình thường.",
    },
    "splenic": {
        "compass_name": "Tiếng nói tức thì của trực giác",
        "rule": "Trực giác của bạn nói một lần, rất nhanh, rất nhẹ — trong vài giây đầu tiên bạn chạm vào tình huống. Nói xong là im. Vấn đề không phải bạn nghe không thấy, mà là bạn hay quay lại hỏi cả hội đồng sau đó, rồi làm chìm tiếng đầu tiên đi.",
        "steps": [
            "Nhận ra cảm giác 'đúng/sai' trong 3 giây đầu — nó đến như một sự thật, không như một ý kiến.",
            "Ghi lại ngay bằng một câu, trước khi thêm bớt: 'Mình thấy: ...'",
            "Chia sẻ với đúng một người đáng tin nếu cần — nhưng quyết định thuộc về cái cảm giác đó, không phải về số đông.",
        ],
        "scenario_business": "Vừa ngồi vào bàn chuyện hợp tác, 30 giây đầu bạn thấy 'không ổn' dù mọi thứ nghe rất hợp lý? Cảm giác đó là dữ liệu. Hãy nói 'mình cần một buổi tối', rồi sáng hôm sau kiểm tra lại: nếu cái 'không ổn' đã mất, nó chỉ là mệt; nếu vẫn còn, đó là câu trả lời.",
        "scenario_purchase": "Cảm giác 'không' lúc chạm tay vào món hàng — dù giá rất hời? Đừng bắt mình hợp lý hóa. Trực giác của bạn không đàm phán giá; nó báo 'nó không thuộc về mình'. Tin nó, bạn tiết kiệm được cả tiền lẫn năng lượng.",
    },
    "ego": {
        "compass_name": "Ý chí của trái tim — cam kết không cần chứng minh",
        "rule": "Cơ quan ra quyết định của bạn là ý chí (Heart/Ego) — khả năng cam kết và đi đến cùng. La bàn chỉ đúng khi bạn cam kết vì mình THẬT SỰ MUỐN, không phải để chứng minh giá trị với ai. Cam kết kiểu 'chứng minh' thì bền ba tháng; cam kết kiểu 'tự nguyện' thì bền cả thập kỷ.",
        "steps": [
            "Trước khi gật đầu, tách hai giọng trong đầu: 'mình muốn' và 'mình phải thắng/chứng minh'. Chỉ tiếp tục khi giọng thứ nhất còn lại.",
            "Hình dung đến ĐOẠN KẾT của cam kết, không phải lễ khởi động: nếu bạn vẫn sẵn sàng ở đoạn khó nhất, đó là cam kết thật.",
            "Một khi cam kết, hãy đi đến cùng — và học cách rút cam kết khi phát hiện nó sinh ra từ giọng 'phải chứng minh'.",
        ],
        "scenario_business": "Được mời dẫn một dự án lớn, và tim đập nhanh vì 'đây là cơ hội chứng minh mình'? Hãy hỏi: nếu không ai biết mình làm, mình vẫn làm không? Nếu câu trả lời trung thực là 'không' — đó là lời mời cho bản ngã, không phải cho bạn. Cảm ơn và từ chối nhẹ nhàng là một động tác ý chí đúng chuẩn.",
        "scenario_purchase": "Muốn mua thứ 'để người ta thấy mình có gu'? Hãy tự hỏi: mình có dùng nó trong đời thường, khi không ai nhìn, không? Ý chí của bạn chỉ nên chi tiền cho những gì bạn sẽ ở bên mỗi ngày.",
    },
    "self_projected": {
        "compass_name": "Giọng nói cần một người lắng nghe",
        "rule": "Ý tưởng của bạn chỉ trở nên rõ khi được nói thành tiếng trước một người đáng tin. Trước đó, nó là 'sương mù trong đầu' — bình thường, không phải bạn dở. Bạn không thiếu quyết đoán; bạn chỉ cần đúng một 'gương âm thanh' để kim la bàn định hình.",
        "steps": [
            "Đặt câu hỏi thành lời cho đúng một người bạn tin — không phải để xin lời khuyên, mà để nghe chính mình nói.",
            "Trong lúc nghe họ phản hồi, quan sát cơ thể: căng xuống hay mở ra? Im lặng hay muốn nói thêm?",
            "Nếu sau vài cuộc 'nói thành tiếng' vẫn lung lay, đó là dấu hiệu câu hỏi đang chờ một mảnh thông tin khác — đừng vội chốt.",
        ],
        "scenario_business": "Lời mời hợp tác khiến bạn 'nóng trong người nhưng chưa rõ'? Hãy nói to: 'Mình đang nghĩ đến việc nhận, nhưng mình muốn nói ra cho bạn nghe trước đã.' Ngay khi nghe mình tự mô tả vai trò, bạn sẽ biết: đó là vai diễn của mình, hay vai diễn của người khác mà mình đang thử mặc.",
        "scenario_purchase": "Đứng giữa hai lựa chọn khó (đặc biệt là chuyện quan hệ): kể lại tình huống cho một người trung lập, và NGHE MÌNH KỂ. Nơi bạn ngập ngừng, nơi bạn nói nhanh hơn, nơi giọng bạn sáng lên — đó là bản đồ quyết định thật của bạn.",
    },
    "mental": {
        "compass_name": "Bản đồ môi trường & hội đồng tư vấn",
        "rule": "Bạn không có 'trạm la bàn' bên trong cố định — và đó là thiết kế, không phải khiếm khuyết. Kim la bàn của bạn nằm ở MÔI TRƯỜNG ĐÚNG + những người TỪNG ĐI ĐƯỜNG ĐÓ. Câu hỏi đúng, đặt trong bối cảnh đúng, sẽ tự hiện ra câu trả lời. Trí tuệ của bạn rất sắc — nhưng nó là bản đồ, không phải người lái.",
        "steps": [
            "Viết câu hỏi của mình thật đúng — một câu, đủ cụ thể để người khác trả lời được.",
            "Tìm 2-3 người đã đi đoạn đường đó (không phải người giỏi nói chung) và hỏi đúng câu đã viết.",
            "Sau khi nghe, quay lại một nơi tĩnh và kiểm tra: câu trả lời nào 'nghe như thật của mình'? Đó là lúc bản đồ gặp người lái.",
        ],
        "scenario_business": "Được mời vào một thương vụ mới? Hãy làm đúng theo thiết kế: liệt kê 2-3 người từng làm thương vụ tương tự, và hỏi họ ĐÚNG câu 'anh/chị sẽ làm gì ở vị trí của em bây giờ?'. Sau đó, tự mình tổng hợp — và chỉ chốt khi bản tổng hợp đó không còn tự sinh ra lý do mới mỗi ngày.",
        "scenario_purchase": "Trước quyết định mua lớn (nhà, xe, khóa dài hạn): hãy sống 'giả lập' với nó trong 1-2 tuần — đi qua con đường đó, dùng thử, ở trong không gian đó. Môi trường đúng sẽ trả lời câu hỏi mà não bạn không trả lời nổi.",
    },
    "lunar": {
        "compass_name": "Chu kỳ trăng 28 ngày — la bàn của nhịp dài",
        "rule": "La bàn của bạn không phải một 'trạm' mà là một CHU KỲ: một vòng trăng (~28-29 ngày). Bạn là người duy nhất trong các Type được 'đo bằng tháng' thay vì bằng phút. Mọi quyết định quan trọng đều chờ được một vòng trăng — và đó là lợi thế, không phải chậm chạp.",
        "steps": [
            "Khi một quyết định lớn xuất hiện, ghi lại ngày đó — đó là 'điểm khởi đầu của vòng quan sát'.",
            "Trong 28 ngày, quan sát ba thứ: năng lượng của mình lên/xuống khi nào, cảm giác với lựa chọn đó ở đầu và cuối chu kỳ, và điều gì lặp lại.",
            "Ở ngày 25-28, đọc lại ghi chú đầu tiên và ra quyết định. Đây là lúc 'sâu gương' của bạn trong nhất.",
        ],
        "scenario_business": "Lời mời hợp tác đến sớm? Bạn được phép trả lời: 'Mình làm việc theo chu kỳ quan sát, mình sẽ trả lời trước khi hết vòng trăng này.' Người nghiêm túc sẽ tôn trọng; người không nghiêm túc sẽ tự lộ ra — và đó là một bộ lọc miễn phí.",
        "scenario_purchase": "Muốn mua một thứ lớn? Hãy chờ đủ một vòng trăng: nếu sau 28 ngày bạn vẫn nghĩ đến nó với cùng một mức 'cần' — mua. Nếu cảm giác đã phai, bạn vừa tiết kiệm được một cái hối hận.",
    },
}

# ---------------------------------------------------------------------------
# 9 CENTERS — Phần 3: "Tháo gỡ gánh nặng"
# ---------------------------------------------------------------------------

CENTER_ORDER: tuple[str, ...] = (
    "Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root",
)

CENTER_LANGUAGE: dict[str, dict[str, str]] = {
    "Head": {
        "life_name": "Trạm phát minh — nơi câu hỏi ra đời",
        "defined_life": "Đầu bạn liên tục nảy ý tưởng: bạn không cần ai đưa đề bài, bạn tự sinh ra việc để giải. Động cơ nội tại đó là tài sản — bạn không bao giờ thiếu việc để nghĩ, chỉ cần đủ người chịu nghe.",
        "open_life": "Đầu của bạn là chiếc bọt biển của những ý nghĩ: dễ hút toan tính, lo âu của người khác thành 'chuyện của mình', rồi mất ngủ vì những vấn đề không thuộc về mình.",
        "open_question": "Ý nghĩ xoay vòng này — là của tôi, hay của người vừa nói với tôi hôm nay?",
        "not_self_life": "Lo lắng không ngơi: đầu chạy số ca khi không có việc thật để tính.",
    },
    "Ajna": {
        "life_name": "Trạm rõ hình — nơi ý tưởng thành hình",
        "defined_life": "Ý tưởng của bạn có khả năng 'chuyển thể': từ mơ hồ thành kế hoạch, từ kế hoạch thành hình rõ mà người khác nhìn thấy được. Đây là tài năng hiếm — nhiều người có ý tưởng, nhưng ít người khiến ý tưởng 'hiện hình'.",
        "open_life": "Đầu tư duy của bạn là chiếc bọt biển của niềm tin: dễ nhuộm màu bởi suy nghĩ của người khác, rồi sống trong một 'thế giới quan' chưa chắc là của mình.",
        "open_question": "Niềm tin này là của tôi, hay tôi mượn từ người mà tôi tin?",
        "not_self_life": "Rối trí, phân vân: hai ý tưởng ngược nhau cùng 'đúng' trong đầu.",
    },
    "Throat": {
        "life_name": "Trạm phát ngôn — nơi lời nói thành sự thật",
        "defined_life": "Bạn nói được và làm được: lời của bạn có trọng lượng, và khi bạn cam kết bằng lời, nó thành ra. Trong một nhóm, đây là trung tâm 'biến ý tưởng thành hiện thực'.",
        "open_life": "Cổ họng của bạn là chiếc bọt biển của ngôn ngữ: dễ nói theo năng lượng của người khác — nhận lời khi người kia hào hứng, im lặng khi người kia im, rồi tự hỏi sau đó 'mình vừa nói gì vậy?'",
        "open_question": "Lời này phát ra vì mình muốn nói, hay vì không khí đang đòi mình phải nói?",
        "not_self_life": "Vụng về lời nói: nói rồi quên, nhận lời rồi không nhớ mình đã nhận.",
    },
    "G": {
        "life_name": "Trạm kim chỉ nam — nơi ý chí định hướng",
        "defined_life": "Bạn biết mình muốn đi đâu: mục tiêu và ý chí rõ, không cần người khác xác nhận là 'đủ giỏi'. Đây là la bàn nội tại mạnh nhất — một khi đã chốt hướng, bạn đi rất bền.",
        "open_life": "Trạm định hướng của bạn là chiếc bọt biển của mục đích: dễ hút 'mục tiêu' của người khác thành của mình, chạy theo người ta, rồi kiệt mà không biết mình đang chạy về đâu.",
        "open_question": "Con đường này là của mình, hay mình đang chạy theo la bàn của người khác?",
        "not_self_life": "Mệt mỏi kéo dài: không phải thiếu ngủ, mà là thiếu 'lý do' rõ để đi.",
    },
    "Heart": {
        "life_name": "Trạm khởi động — nơi cam kết thành hiện thực",
        "defined_life": "Bạn có khả năng biến cam kết thành hành động thực: khi đã gật đầu, bạn đi đến cùng. Đây là trung tâm của 'người giữ lời' — và trong một nhóm, họ là người khiến dự án 'ra đi'.",
        "open_life": "Trạm ý chí của bạn là chiếc bọt biển của cam kết: dễ nhận lời vì cảm xúc lúc đó, vì muốn được yêu quý, hoặc vì 'người ta đang cần' — rồi cạn sạch ở giữa chừng.",
        "open_question": "Mình cam kết vì mình muốn, hay vì sợ từ chối làm người ta thất vọng?",
        "not_self_life": "Cạn sạch: không còn gì để cho, kể cả với chính mình.",
    },
    "Spleen": {
        "life_name": "Trạm an toàn — nơi trực giác bảo vệ bạn",
        "defined_life": "Bạn có 'phản xạ sinh tồn' nhạy: biết không gian nào an toàn, người nào đáng tin, chuyện nào nên tránh — thường trước cả khi lý trí kịp phân tích. Đây là bản năng chọn môi trường sống đúng.",
        "open_life": "Trạm an toàn của bạn là chiếc bọt biển của cảm giác: dễ hút sự bất an của môi trường thành 'mình thấy lạ, mình thấy sợ', rồi chọn sai chỗ đứng vì năng lượng của người khác.",
        "open_question": "Cảm giác 'không an toàn' này phát ra từ mình, hay từ không gian mình đang đứng?",
        "not_self_life": "Sợ hãi, hoảng: tim đập nhanh trước những thứ chưa xảy ra.",
    },
    "Sacral": {
        "life_name": "Trạm nhiên liệu — nơi việc làm được nuôi",
        "defined_life": "Bạn có thùng nhiên liệu liên tục: việc lặp lại, thủ công, cần tập trung — càng làm càng có sức, không cần động lực từ bên ngoài. Đây là quà hiếm: nhiều người làm việc vì muốn thoát, bạn làm việc vì việc.",
        "open_life": "Trạm nhiên liệu của bạn là chiếc bọt biển của 'việc phải làm': dễ làm việc vì áp lực, vì cảm xúc, vì người khác đang nhìn — chứ không phải vì tín hiệu 'ừ ừ' thật từ vùng thượng vị.",
        "open_question": "Mình đang làm việc này vì nó gọi mình, hay vì mình đang bị nó gọi?",
        "not_self_life": "Kiệt quệ: làm nhiều mà không thấy 'được nạp' — dấu hiệu việc không hợp nhiên liệu.",
    },
    "Solar Plexus": {
        "life_name": "Trạm thấu cảm — nơi cảm xúc được chuyển hóa",
        "defined_life": "Bạn có chiều sâu cảm xúc hiếm có: người khác ở cạnh bạn thấy 'an toàn để thật', và bạn giữ được cân bằng khi cảm xúc của họ tràn qua. Đây là trung tâm của 'người chữa lành bằng sự hiện diện'.",
        "open_life": "Trạm cảm xúc của bạn là chiếc bọt biển sâu nhất: bạn hấp thu cảm xúc của người xung quanh thành cảm xúc của mình, rồi mang theo chúng về nhà — và tự hỏi 'mình sao tự nhiên buồn thế?'",
        "open_question": "Cảm xúc này — mình đang cảm, hay mình đang mang hộ ai?",
        "not_self_life": "Nỗi sợ, đấu tranh nội tâm: luôn thấy có điều gì đó 'sai sai' mà không nói được tên.",
    },
    "Root": {
        "life_name": "Trạm nhịp — nơi động lực mỗi ngày ra đời",
        "defined_life": "Bạn thức dậy với nhịp của riêng mình: động lực đến tự nhiên, không cần ai thúc. Đây là quà của 'người tự đánh thức bản thân' — trong một nhóm, nhịp của bạn kéo cả phòng đi cùng.",
        "open_life": "Trạm nhịp của bạn là chiếc bọt biển của lịch trình: dễ bị cuốn vào tốc độ của người khác, chạy nhanh theo họ, rồi một ngày nào đó dừng lại và nhận ra mình đã lâu chưa biết mình thích nhịp nào.",
        "open_question": "Nhịp vội vã này là của mình, hay mình đang chạy theo lịch của ai đó?",
        "not_self_life": "Lo âu, vội vàng: luôn có một 'chuyến tàu sắp chạy' dù chẳng có tàu nào cả.",
    },
}

# ---------------------------------------------------------------------------
# 12 PROFILE — Phần 4: "Vai diễn cuộc đời"
# ---------------------------------------------------------------------------

PROFILE_STORIES: dict[str, dict[str, str]] = {
    "1/3": {
        "story_name": "Người nghiên cứu sâu & người đi tiên phong liều lĩnh",
        "inner_life": "Bên trong là người quan sát kỹ, cần hiểu cho thấu đáo mới dám động — và đôi khi chờ đến mức cơ hội trôi mất.",
        "outer_life": "Bên ngoài lại là người dám búng tay đầu tiên, bắt tay vào làm trước khi ai kịp lên kế hoạch.",
        "mistake_reframe": "Những lần vấp của bạn không phải thất bại — đó là cách thiết kế của bạn học nhanh hơn ai: 'tôi chưa hiểu hết' chính là bài học, và bạn luôn có quyền thử lần hai.",
    },
    "1/4": {
        "story_name": "Người nghiên cứu & người quan sát mạng lưới",
        "inner_life": "Bạn thích đào một cái giếng đến tận nước, thay vì mười cái hố cạn.",
        "outer_life": "Bạn học giỏi nhất từ việc quan sát người khác — thành công lẫn vấp ngã của họ đều là dữ liệu miễn phí cho bạn.",
        "mistake_reframe": "Khi bạn thấy mình 'quá chậm so với mọi người', đó chỉ là nhầm thước đo: thiết kế của bạn đo bằng độ sâu, không bằng tốc độ.",
    },
    "2/4": {
        "story_name": "Người lặng lẽ & người mở đường cơ hội",
        "inner_life": "Bên trong bạn rất riêng tư, cần không gian để hiểu mình — gần gũi kiểu chia sẻ từng chút một, không phải kiểu 'mở hết ra ngay'.",
        "outer_life": "Bên ngoài bạn lại có sức hút mở các con đường: đúng người, đúng cơ hội cứ tự tìm đến bạn.",
        "mistake_reframe": "Nếu quá khứ để lại cảm giác 'mình khó thân', sự thật là bạn chọn lọc kết nối — ít mà bền, đó là thiết kế chứ không phải khiếm khuyết.",
    },
    "2/5": {
        "story_name": "Người ẩn sĩ & người chinh phục từ xa",
        "inner_life": "Bạn cần những khoảng lặng dài để tái tạo; 'biến mất' một thời gian không phải trốn tránh, mà là cách bạn nạp pin.",
        "outer_life": "Khi xuất hiện, bạn có từ trường rõ — người ta nhớ bạn vì sự riêng biệt, không phải vì bạn nói nhiều.",
        "mistake_reframe": "Những lần bạn rút lui bị hiểu nhầm là lạnh nhạt? Thiết kế của bạn học cách 'ra hiệu' trước khi biến mất — chỉ cần một câu, mọi người sẽ tôn trọng nhịp của bạn.",
    },
    "3/5": {
        "story_name": "Nhà thám hiểm va vấp & chuyên gia giải cứu thực chiến",
        "inner_life": "Bên trong là người học bằng cách đâm đầu vào: thử, vấp, rút kinh nghiệm — sách vở chỉ là phần phụ.",
        "outer_life": "Bên ngoài là người chuyên 'chạy đến cứu' khi mọi thứ rối; bạn giỏi nhất ở trạng thái khẩn cấp.",
        "mistake_reframe": "Danh sách thất bại của bạn thực chất là phòng thí nghiệm: mỗi lần va vấp là một thí nghiệm thành công về việc 'đường này không đi được'.",
    },
    "3/6": {
        "story_name": "Nhà thám hiểm & người xây hệ thống",
        "inner_life": "Bạn học qua thử-sai, nhưng luôn có trực giác 'cái nào đáng đầu tư'.",
        "outer_life": "Bạn có sức mạnh biến trải nghiệm hỗn loạn thành quy trình: đi trước, rồi dọn đường cho người khác đi sau.",
        "mistake_reframe": "Khi một dự án tan, đừng tự hỏi 'mình sai ở đâu' — hãy hỏi 'mình học được gì để lần sau xây chắc hơn'. Vết sứt mẻ là dữ liệu thi công.",
    },
    "4/6": {
        "story_name": "Người phục hồi & người kiến tạo thực chiến",
        "inner_life": "Bên trong mang vết sẹo và bài học — bạn hiểu 'nghiêm túc' là gì vì đã trả giá.",
        "outer_life": "Bên ngoài là người xây dựng bền bỉ: bạn không sợ việc khó, bạn sợ việc vô nghĩa.",
        "mistake_reframe": "Những tổn thương cũ không phải gánh nặng — chúng là bản đồ địa hình: chính chỗ đau nhất năm xưa là nơi bạn bây giờ giúp được người khác rõ nhất.",
    },
    "4/1": {
        "story_name": "Người phục hồi & người dẫn đường qua bão",
        "inner_life": "Bạn đã đi qua những đoạn đường dài đầy tổn thương và vẫn đứng được — đó là căn cước của bạn.",
        "outer_life": "Khi cuộc đời giông bão, bạn là kiểu người mà cả nhóm quay lại để hỏi: 'rồi mình làm gì tiếp?'",
        "mistake_reframe": "Cứ nghĩ 'giá như ngày xưa không...'? Thiết kế của bạn không đi đường tắt: chính những khúc quanh ấy đã rèn ra cái mà giờ bạn dùng để dẫn đường.",
    },
    "5/1": {
        "story_name": "Người chinh phục & người dẫn lối",
        "inner_life": "Bạn có từ trường thu hút — không cần quảng cáo, người ta vẫn muốn ở gần.",
        "outer_life": "Bạn sinh ra để mở hướng đi mới và kéo người khác theo, ở tầm nhìn xa hơn một nước đi.",
        "mistake_reframe": "Khi cảm giác 'mình phải tỏa sáng liên tục' ập đến, đó là lúc nghỉ: sức mạnh của bạn nằm ở chất, không ở tần suất xuất hiện.",
    },
    "5/2": {
        "story_name": "Người chinh phục & người quan sát",
        "inner_life": "Bạn thu hút sự chú ý, nhưng điều bạn thực sự thích là quan sát: ai là ai, họ đến vì điều gì.",
        "outer_life": "Sự hiện diện của bạn làm người khác muốn bộc lộ thật — bạn là 'mặt gương đẹp' mà họ muốn soi.",
        "mistake_reframe": "Nếu bạn từng bị đánh giá là 'nhiều bí ẩn, khó đọc' — hãy thêm một bước: chia sẻ một điều nhỏ về mình trước, cánh cửa sẽ mở hai chiều.",
    },
    "6/2": {
        "story_name": "Người kiến tạo & người kết nối",
        "inner_life": "Bên trong là người xây: bạn muốn tạo ra thứ gì đó có thật, sờ được, sống được.",
        "outer_life": "Bên ngoài bạn giỏi nối người với người — bạn là 'cầu nối' tự nhiên trong mọi nhóm.",
        "mistake_reframe": "Khi bạn kiệt vì 'ai cũng cần mình lo', thiết kế nhắc bạn: bạn xây cho mình trước, rồi mới xây cho người khác — trụ phải vững trước khi làm mái.",
    },
    "6/3": {
        "story_name": "Người kiến tạo & người mở màn",
        "inner_life": "Bạn có tay nghề và ý tưởng 'từ trong ra ngoài': làm xong rồi mới nói, và làm thì phải cho ra hàng.",
        "outer_life": "Bạn là người dám bấm nút 'bắt đầu' trước cả khi kế hoạch đủ đầy — thị trường thường thưởng cho những ai mở màn sớm.",
        "mistake_reframe": "Mỗi lần 'ra mắt rồi phải sửa' không làm bạn thất bại — với thiết kế của bạn, hoàn thiện là một vòng xoáy, không phải một đích đến.",
    },
}

# ---------------------------------------------------------------------------
# 36 CHANNELS — tên song ngữ + một câu đời sống (theo knowledge/03_36_kenh.md)
# ---------------------------------------------------------------------------

CHANNEL_LANGUAGE: dict[str, dict[str, str]] = {
    "1-8": {"name": "Hình mẫu sáng tạo (Inspiration)", "life": "Bạn đóng góp bằng sự khác biệt thật của chính mình — không cần giống ai."},
    "2-14": {"name": "Người giữ chìa khóa (Beat)", "life": "Phương hướng đúng mở ra qua nhịp cơ thể, không qua phân tích."},
    "3-60": {"name": "Đột biến (Mutation)", "life": "Năng lượng thay đổi theo nhịp lúc có lúc không — ép đều đặn là đi ngược thiết kế."},
    "4-63": {"name": "Logic", "life": "Mọi ý tưởng đều phải qua cửa nghi ngờ: chứng minh được mới thật sự là của bạn."},
    "5-15": {"name": "Nhịp điệu (Rhythm)", "life": "Bạn khỏe nhất khi sống đúng nhịp riêng — giờ giấc, thói quen là tài sản."},
    "6-59": {"name": "Thân mật (Intimacy)", "life": "Ranh giới và sự thân mật học qua nhau: mở đúng người, đóng đúng lúc."},
    "7-31": {"name": "Lãnh đạo (Alpha)", "life": "Vai trò dẫn dắt đến tự nhiên khi cộng đồng công nhận bạn."},
    "9-52": {"name": "Tập trung (Concentration)", "life": "Khả năng tập trung sâu và bền khi việc đó thật sự đáng làm."},
    "10-20": {"name": "Thức tỉnh (Awakening)", "life": "Sống tỉnh thức và truyền sự tỉnh thức qua chính cách bạn hiện diện."},
    "10-34": {"name": "Khám phá niềm tin (Exploration)", "life": "Bạn đi theo niềm tin của chính mình, không theo số đông."},
    "10-57": {"name": "Hình thức hoàn hảo (Perfected Form)", "life": "Bản năng hoàn thiện cách mình sống và làm — đẹp và đúng."},
    "11-56": {"name": "Tò mò (Curiosity)", "life": "Người kể chuyện: gom ý tưởng và trải nghiệm, rồi kể lại thành câu chuyện."},
    "12-22": {"name": "Cởi mở (Openness)", "life": "Cảm xúc cần được lắng nghe trước khi cất lời — im lặng đúng lúc cũng là tài năng."},
    "13-33": {"name": "Người kể chuyện (Prodigal)", "life": "Biến trải nghiệm của mình và của người khác thành bài học chia sẻ được."},
    "16-48": {"name": "Tài năng (Wavelength)", "life": "Tài năng sâu lên qua lặp lại: kiên trì là chìa khóa, không phải cảm hứng."},
    "17-62": {"name": "Tổ chức (Acceptance)", "life": "Biến ý kiến thành cấu trúc rõ ràng, chi tiết và dùng được."},
    "18-58": {"name": "Hoàn thiện (Judgement)", "life": "Thấy chỗ chưa hoàn thiện để sửa cho tốt hơn — và học cách tận hưởng thành quả."},
    "19-49": {"name": "Nhạy cảm (Synthesis)", "life": "Nhạy với nhu cầu và nguyên tắc — biết khi nào nên giữ, khi nào nên đổi thay."},
    "20-34": {"name": "Sức hút (Charisma)", "life": "Biến nhận thức thành hành động ngay — bận rộn đúng việc thì bạn tỏa sáng."},
    "20-57": {"name": "Sóng não (Brainwave)", "life": "Trực giác xuyên thấu trong hiện tại, và bạn nói ra được cho người khác."},
    "21-45": {"name": "Dòng tiền (Money Line)", "life": "Tài năng vật chất rõ: tạo giá trị, kiểm soát nguồn lực, nuôi bộ lạc của mình."},
    "23-43": {"name": "Thiên tài cấu trúc (Structuring)", "life": "Insight cá nhân 'không giống ai' — khi được mời nói, nó thay đổi cuộc chơi."},
    "24-61": {"name": "Nhận thức (Awareness)", "life": "Áp lực phải hiểu điều chưa ai hiểu — món quà của bạn là câu hỏi đúng."},
    "26-44": {"name": "Thuyết phục (Surrender)", "life": "Người truyền đạt bẩm sinh: kể đúng câu chuyện, với đúng người, đúng lúc."},
    "27-50": {"name": "Bảo tồn (Preservation)", "life": "Bản năng bảo vệ, chăm sóc và giữ giá trị cho những gì quan trọng."},
    "28-38": {"name": "Đấu tranh (Struggle)", "life": "Đấu tranh tìm ý nghĩa — bướng bỉnh đúng chỗ sẽ thành sức mạnh."},
    "29-46": {"name": "Khám phá (Discovery)", "life": "Cam kết đi đến cùng nơi người khác bỏ cuộc — thành công qua trải nghiệm."},
    "30-41": {"name": "Khao khát trải nghiệm (Recognition)", "life": "Cảm xúc tập trung vào điều mới — khao khát là nhiên liệu, không phải mệnh lệnh."},
    "32-54": {"name": "Biến đổi (Transformation)", "life": "Tham vọng lành mạnh: liên tục nâng cấp bản thân và con đường mình đi."},
    "35-36": {"name": "Phù du (Transitoriness)", "life": "Đa trải nghiệm, đa tài — bài học là ở lại đủ lâu để hái quả."},
    "37-40": {"name": "Cộng đồng (Community)", "life": "Xây cộng đồng bằng thỏa thuận rõ ràng và sự chăm sóc đôi bên."},
    "39-55": {"name": "Tâm trạng (Emoting)", "life": "Cảm xúc sâu và lãng mạn — cần người nghe, không cần ai sửa."},
    "42-53": {"name": "Trưởng thành (Maturation)", "life": "Bắt đầu đúng và đi đến chín muồi — biết kết thúc cũng là một tài năng."},
    "47-64": {"name": "Trừu tượng (Abstraction)", "life": "Xử lý quá khứ thành minh mẫn — đi từ nhầm lẫn đến rõ ràng."},
    "34-57": {"name": "Sức mạnh (Power)", "life": "Sức mạnh sinh tồn bản năng — tin vào trực giác về nhịp của chính mình."},
    "25-51": {"name": "Khởi xướng (Initiation)", "life": "Cần là người đầu tiên: khởi xướng bằng tình yêu, không bằng ganh đua."},
}


def vn_channel(gate1: int | str, gate2: int | str) -> dict[str, str] | None:
    """Look up channel language by either gate order (canonical = ascending)."""
    lo, hi = sorted((int(gate1), int(gate2)))
    return CHANNEL_LANGUAGE.get(f"{lo}-{hi}")


# ---------------------------------------------------------------------------
# DEFINITION (4) — Phần 4
# ---------------------------------------------------------------------------

DEFINITION_LANGUAGE: dict[str, str] = {
    "Single Definition": "Một khối năng lượng liền mạch — bạn tự vận hành và trọn vẹn trong chính mình. Mối quan hệ với bạn là 'đôi bạn đồng hành', không phải 'hai mảnh ghép của nhau'.",
    "Split Definition": "Hai cụm năng lượng song song — bạn xử lý đời theo hai nhịp, và cần quan hệ để nhìn thấy các mặt của mình, nhưng không cần ai đó để tồn tại.",
    "Triple Split Definition": "Ba cụm năng lượng — bạn cần không gian, người và thời gian vừa đủ để 'tiêu hóa' cuộc sống. Đổ đầy lịch liên tục là cách nhanh nhất làm bạn ùn tắc.",
    "Quadruple Split Definition": "Bốn cụm năng lượng — bạn đa nhiệm bẩm sinh; bài học suốt đời là học cách xếp ưu tiên, vì bạn không thể (và không cần) làm tất cả cùng lúc.",
}
DEFINITION_FALLBACK = "Định nghĩa mở — bạn là người lấy mẫu từ môi trường để hiểu mình."

# ---------------------------------------------------------------------------
# INCARNATION CROSS — Phần 4
# ---------------------------------------------------------------------------

CROSS_TYPE_LANGUAGE: dict[str, str] = {
    "Left Angle": "Góc trái — cuộc đời bạn vận hành theo chiều sâu: một chủ đề được đào qua nhiều lần trải nghiệm cho đến khi thấu.",
    "Right Angle": "Góc phải — cuộc đời bạn vận hành theo chiều rộng: mở rộng kết nối và trải nghiệm đa dạng.",
    "Juxtaposition": "Song song — cuộc đời bạn là bài học cân bằng hai mặt đối diện.",
}

CROSS_FRAMING = (
    "Chữ thập Hiện thân không phải 'nghề nghiệp phải làm', mà là bài toán lớn mà linh hồn bạn "
    "chọn để trải nghiệm trong kiếp này. Nó giải thích vì sao có những chủ đề cứ quay lại với bạn "
    "— không phải để trừng phạt, mà để bạn học cho đến khi thông."
)

# ---------------------------------------------------------------------------
# PHẦN 5 — Nhật ký thử nghiệm 7 ngày
# ---------------------------------------------------------------------------

_SIGNAL_BY_AUTHORITY: dict[str, str] = {
    "emotional": "mặt phẳng của sóng cảm xúc (sau vài giờ đến vài ngày)",
    "sacral": "tiếng 'ừ ừ' ấm ở vùng thượng vị, trong 2-3 giây đầu",
    "splenic": "cảm giác đúng/sai trong 3 giây đầu tiên",
    "ego": "lòng sẵn sàng cam kết khi không ai biết",
    "self_projected": "cảm giác rõ khi nói thành tiếng với một người đáng tin",
    "mental": "câu trả lời vẫn nguyên sau khi nghe 2-3 người đã đi trước",
    "lunar": "nhịp năng lượng giữ nguyên trong 7 ngày đầu của vòng quan sát",
}


def seven_day_log(authority: str, open_center_count: int) -> list[str]:
    """Three tiny exercises for Part 5, personalized by authority and open centers."""
    key = resolve_authority(authority)
    signal = _SIGNAL_BY_AUTHORITY.get(key, _SIGNAL_BY_AUTHORITY["emotional"])
    exercises = [
        f"Nghe tín hiệu: trong tuần, chọn đúng 3 quyết định nhỏ và trước khi chốt, hỏi la bàn của bạn — {signal}. Ghi lại 3 dòng mỗi quyết định: câu hỏi, tín hiệu nhận được, và mình đã tin nó không?",
        f"Săn bọt biển: {open_center_count} trạm mở của bạn là những 'chiếc bọt biển'. Mỗi tối, bắt được 1 lần mình mang theo cảm xúc không phải của mình, viết 1 dòng: 'Cảm xúc này của ai?'",
        "Nhiên liệu đúng: chọn 1 việc thuộc vùng mạnh (một trung tâm có màu) để làm trọn vẹn trong ngày — và ghi lại khoảnh khắc nào bạn thấy 'đúng nhiên liệu' nhất. Tuần sau, lặp lại chính việc đó.",
    ]
    return exercises

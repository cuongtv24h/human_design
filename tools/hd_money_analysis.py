"""
Human Design Money & Wealth Analysis Tool - Full Money Map
Phân tích dòng tiền, tài chính, business model, pricing, investment theo Type/Profile/Channels

Tích hợp từ knowledge:
- 03_36_kenh.md: 21-45 Money, 26-44 Surrender, 40-37 Community, 32-54 Transformation
- 02_9_trung_tam.md: Heart/Ego center - Ý chí, tiền bạc, vật chất
- 04_5_loai_va_chien_luoc.md: Type strategy
- 12_tham_van_tong_quat_60_bien_the.md: Type deep dive, Profile

5 Types x 12 Profiles = 60 biến thể về tiền
"""

from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER, CHANNEL_TO_CENTERS, CHANNELS
from hd_consultation_general import TYPE_DEEP_DIVE, PROFILE_DEEP_DIVE
from datetime import datetime
import json

# ==================== MONEY CHANNELS ====================
MONEY_CHANNELS = {
    (21, 45): {
        "name": "Money - Dòng tiền Bộ lạc",
        "centers": "Heart-Throat",
        "circuit": "Tribal/Ego",
        "theme": "Quản lý vật chất, kiểm soát, lãnh đạo bộ lạc, dòng tiền",
        "description": "Kênh tiền bạc quan trọng nhất. Gate 21 Control (kiểm soát) + Gate 45 Gatherer (tập hợp). Người có kênh này có khả năng tự nhiên quản lý dòng tiền, kiểm soát tài nguyên, lãnh đạo tài chính bộ lạc. Phù hợp làm CEO, quản lý tài chính, chủ doanh nghiệp.",
        "business": "Phù hợp lãnh đạo, quản lý tiền, định hướng vật chất cho cộng đồng. Cần kiểm soát nhưng không kiểm soát quá mức.",
        "not_self": "Kiểm soát tiền bạc quá mức hoặc không kiểm soát được, vấn đề với quyền lực vật chất."
    },
    (26, 44): {
        "name": "Surrender - Bán hàng & Thuyết phục",
        "centers": "Heart-Spleen",
        "circuit": "Tribal/Ego",
        "theme": "Truyền đạt, thuyết phục, bán hàng, ích kỷ lành mạnh",
        "description": "Kênh bán hàng. Gate 26 Egoist (bán hàng, thuyết phục) + Gate 44 Alertness (nhận diện pattern, quá khứ). Khả năng bán hàng tự nhiên, thuyết phục, kể chuyện. Cần học cách bán hàng trung thực, không thao túng.",
        "business": "Sales, marketing, thuyết trình, đàm phán. Phù hợp bán hàng cao cấp, storytelling.",
        "not_self": "Thao túng, bán hàng không trung thực, hoặc sợ bán hàng."
    },
    (40, 37): {
        "name": "Community - Cộng đồng & Thỏa thuận",
        "centers": "Heart-Solar Plexus",
        "circuit": "Tribal",
        "theme": "Cộng đồng, thỏa thuận, gia đình, chạm, bargain",
        "description": "Kênh cộng đồng. Gate 40 Aloneness (cô đơn, làm việc) + Gate 37 Friendship (tình bạn, thỏa thuận). Năng lượng thỏa thuận, hợp đồng, cộng đồng. Cần cân bằng giữa làm việc và nghỉ ngơi, giữa cho và nhận trong cộng đồng.",
        "business": "Phù hợp xây dựng cộng đồng, membership, thỏa thuận, hợp đồng, gia đình business.",
        "not_self": "Làm việc quá sức cho cộng đồng, hoặc từ chối thỏa thuận."
    },
    (32, 54): {
        "name": "Transformation - Tham vọng & Chuyển hóa",
        "centers": "Spleen-Root",
        "circuit": "Tribal",
        "theme": "Tham vọng, chuyển hóa, động lực cải tiến, kinh doanh",
        "description": "Kênh tham vọng. Gate 32 Continuity (liên tục, đánh giá) + Gate 54 Ambition (tham vọng, drive). Động lực mạnh mẽ để cải tiến, tham vọng, leo thang. Phù hợp kinh doanh, khởi nghiệp, transformation business.",
        "business": "Khởi nghiệp, scale business, transformation, cải tiến liên tục. Cần quản lý tham vọng, không để tham vọng chi phối.",
        "not_self": "Tham vọng không lành mạnh, hoặc sợ tham vọng, sợ thành công."
    },
    (14, 2): {
        "name": "Beat - Tài nguyên & Hướng đi",
        "centers": "Sacral-G",
        "circuit": "Individual",
        "theme": "Tài nguyên, hướng đi, chìa khóa, power skills",
        "description": "Gate 14 Power Skills (kỹ năng quyền lực, tài nguyên) + Gate 2 Direction (hướng đi). Khả năng quản lý tài nguyên, kỹ năng tạo tiền. Gate 14 là một trong những cổng tiền quan trọng - kỹ năng biến tài nguyên thành tiền.",
        "business": "Quản lý tài nguyên, đầu tư, kỹ năng tạo tiền, hướng đi cá nhân.",
        "not_self": "Lãng phí tài nguyên, không có hướng đi."
    },
    (5, 15): {
        "name": "Rhythm - Nhịp điệu & Tài chính đều đặn",
        "centers": "Sacral-G",
        "circuit": "Collective/Logic",
        "theme": "Nhịp điệu, thói quen, dòng tiền đều đặn",
        "description": "Gate 5 Fixed Rhythm + Gate 15 Extremes. Nhịp điệu cố định, thói quen. Phù hợp dòng tiền đều đặn, thói quen tài chính, passive income.",
        "business": "Xây dựng thói quen tài chính, dòng tiền đều đặn, passive income, routine business.",
        "not_self": "Không có nhịp điệu, dòng tiền bấp bênh."
    }
}

# Gates quan trọng cho tiền
MONEY_GATES = {
    21: {"name": "Control - Kiểm soát", "center": "Heart", "money_theme": "Kiểm soát tiền bạc, quản lý, lãnh đạo. Cần học kiểm soát lành mạnh, không kiểm soát quá mức.", "business": "Quản lý, kiểm soát tài chính, lãnh đạo."},
    45: {"name": "Gatherer - Tập hợp", "center": "Throat", "money_theme": "Tập hợp tài nguyên, phân phối cho bộ lạc. Khả năng tập hợp tiền, tài nguyên.", "business": "Tập hợp vốn, phân phối tài nguyên, lãnh đạo cộng đồng."},
    26: {"name": "Egoist - Bán hàng", "center": "Heart", "money_theme": "Thuyết phục, bán hàng, ego. Kỹ năng bán hàng tự nhiên.", "business": "Sales, marketing, thuyết phục."},
    44: {"name": "Alertness - Nhận diện", "center": "Spleen", "money_theme": "Nhận diện pattern, quá khứ, cơ hội. Khả năng nhận diện cơ hội tiền bạc.", "business": "Nhận diện xu hướng, cơ hội đầu tư, pattern thị trường."},
    14: {"name": "Power Skills - Kỹ năng quyền lực", "center": "Sacral", "money_theme": "Một trong những cổng tiền mạnh nhất. Kỹ năng biến tài nguyên thành tiền, quản lý tài nguyên.", "business": "Kỹ năng tạo tiền, quản lý tài nguyên, đầu tư."},
    2: {"name": "Direction - Hướng đi", "center": "G", "money_theme": "Hướng đi, la bàn. Biết hướng đi tài chính.", "business": "Định hướng chiến lược, tầm nhìn."},
    32: {"name": "Continuity - Liên tục", "center": "Spleen", "money_theme": "Đánh giá, liên tục, cải tiến. Khả năng đánh giá dự án tài chính có bền vững không.", "business": "Đánh giá business, due diligence, continuity."},
    54: {"name": "Ambition - Tham vọng", "center": "Root", "money_theme": "Tham vọng, drive, leo thang. Động lực kiếm tiền, tham vọng vật chất.", "business": "Tham vọng kinh doanh, drive, scale."},
    40: {"name": "Aloneness - Cô đơn/Làm việc", "center": "Heart", "money_theme": "Làm việc, nghỉ ngơi, thỏa thuận. Cần cân bằng làm việc và nghỉ ngơi để có tiền bền vững.", "business": "Work-life balance, thỏa thuận làm việc."},
    37: {"name": "Friendship - Tình bạn", "center": "Solar Plexus", "money_theme": "Thỏa thuận, cộng đồng, gia đình. Tiền qua cộng đồng, thỏa thuận.", "business": "Community business, thỏa thuận, gia đình business."},
    5: {"name": "Fixed Rhythm - Nhịp điệu cố định", "center": "Sacral", "money_theme": "Nhịp điệu, thói quen. Dòng tiền đều đặn qua thói quen.", "business": "Thói quen tài chính, passive income."},
    15: {"name": "Extremes - Cực đoan", "center": "G", "money_theme": "Cực đoan, nhịp điệu, tình yêu nhân loại. Cần nhịp điệu tài chính đa dạng.", "business": "Đa dạng dòng tiền."},
    19: {"name": "Wanting - Muốn", "center": "Root", "money_theme": "Nhu cầu, muốn, nhạy cảm. Nhu cầu vật chất, tiền bạc.", "business": "Hiểu nhu cầu thị trường."},
    49: {"name": "Revolution - Cách mạng", "center": "Solar Plexus", "money_theme": "Cách mạng, nguyên tắc, từ chối. Nguyên tắc về tiền bạc.", "business": "Nguyên tắc tài chính, cách mạng mô hình."},
}

# Money strategy theo Type
TYPE_MONEY_STRATEGY = {
    "Manifestor": {
        "money_aura": "Aura đóng, đẩy - Bạn không thu hút tiền bằng cách chờ đợi, mà bằng cách KHỞI XƯỚNG và THÔNG BÁO. Tiền đến khi bạn khởi xướng dự án mới và thông báo cho người khác.",
        "how_to_attract": [
            "Khởi xướng dự án, ý tưởng mới về tiền - Bạn là người bắt đầu dòng tiền",
            "Thông báo trước khi hành động về tiền: 'Tôi sẽ đầu tư vào X', 'Tôi sẽ tăng giá lên Y'",
            "Đừng chờ đợi, đừng đáp ứng - Hãy khởi xướng",
            "Tiền đến từ việc tạo ra tác động, khởi xướng xu hướng mới",
            "Làm việc theo đợt bộc phát - Có thể kiếm tiền lớn trong thời gian ngắn, rồi nghỉ ngơi"
        ],
        "pricing": "Định giá cao, premium. Bạn mang năng lượng khởi xướng hiếm (9%), đừng bán rẻ. Giá phản ánh tác động bạn tạo ra, không phải giờ làm việc. Phù hợp mô hình: High-ticket, consulting, khởi nghiệp.",
        "business_model": ["Khởi nghiệp, founder", "Consulting cao cấp, high-ticket", "Sản phẩm đột phá, tiên phong", "Tự chủ cao, không thích bị quản lý"],
        "money_traps": [
            "Cố gắng làm việc như Generator (8h/ngày bền bỉ) -> kiệt sức, mất tiền",
            "Không thông báo về tiền -> gặp phản kháng, mất cơ hội",
            "Giận dữ về tiền -> Not-Self Anger khi bị kiểm soát tài chính",
            "Bị kiểm soát tài chính bởi người khác -> mất tự do"
        ],
        "investment": "Đầu tư theo đợt bộc phát, theo trực giác khởi xướng. Không phù hợp đầu tư đều đặn nhỏ giọt như Generator. Phù hợp đầu tư lớn vào ý tưởng đột phá bạn tin tưởng. Cần thông báo cho đối tác/gia đình trước khi đầu tư lớn.",
        "saving_spending": "Tiêu tiền theo đợt bộc phát, cần học quản lý. Tiết kiệm cho giai đoạn nghỉ ngơi sau khi khởi xướng."
    },
    "Generator": {
        "money_aura": "Aura mở, hút - Bạn là thỏi nam châm thu hút tiền khi làm việc bạn YÊU. Tiền đến khi Sacral nói uh-huh với cơ hội.",
        "how_to_attract": [
            "Chờ để Đáp Ứng cơ hội tiền bạc - Đừng khởi xướng việc kiếm tiền",
            "Lắng nghe Sacral: uh-huh (mở, cao, ngực nở) = CÓ với cơ hội tiền, uh-uh (đóng, thấp) = KHÔNG",
            "Làm việc bạn YÊU - Sacral sẽ cho năng lượng vô tận để kiếm tiền",
            "Hỏi câu hỏi có/không về tiền: 'Bạn có muốn đầu tư vào X không?' thay vì 'Bạn muốn đầu tư gì?'",
            "Kiên nhẫn - Tiền đến từ việc làm đúng việc, không phải làm nhiều việc"
        ],
        "pricing": "Định giá theo giá trị bạn tạo ra khi làm việc bạn yêu. Khi bạn hài lòng (Satisfaction), bạn tạo ra giá trị lớn. Đừng định giá theo giờ, định giá theo kết quả. Phù hợp: Value-based pricing, làm việc bền bỉ với khách hàng yêu thích.",
        "business_model": ["Làm việc bền bỉ, xây dựng lâu dài", "Nghề thủ công, chuyên môn sâu", "Bất kỳ việc gì BẠN YÊU - Sacral cho năng lượng vô tận", "Phù hợp làm việc cho công ty, hoặc freelancer với khách hàng yêu thích"],
        "money_traps": [
            "Làm việc không yêu thích để kiếm tiền -> Frustration + kiệt sức Sacral + mất tiền",
            "Khởi xướng cơ hội tiền bạc thay vì đáp ứng -> sai thiết kế",
            "Quyết định tiền bạc bằng đầu óc thay vì Sacral",
            "Làm việc quá sức như MG nhanh -> kiệt sức"
        ],
        "investment": "Đầu tư vào điều bạn YÊU và hiểu rõ. Sacral uh-huh với khoản đầu tư. Đầu tư bền bỉ, dài hạn, đều đặn. Phù hợp DCA (dollar-cost averaging) vào thứ bạn yêu. Đừng đầu tư theo trend nếu Sacral uh-uh.",
        "saving_spending": "Tiết kiệm tự nhiên khi làm việc bạn yêu (Satisfaction). Tiêu tiền cho điều mang lại Satisfaction. Học cách nói uh-uh với chi tiêu không mang lại Satisfaction."
    },
    "Manifesting Generator": {
        "money_aura": "Aura mở, nhanh, đa nhiệm - Bạn thu hút tiền bằng tốc độ, hiệu quả, đa dạng. Tiền đến từ nhiều nguồn, nhiều dòng.",
        "how_to_attract": [
            "Chờ Đáp Ứng như Generator, rồi Thông Báo như Manifestor",
            "Bước 1: Chờ tín hiệu tiền bạc, lắng nghe Sacral uh-huh/uh-uh",
            "Bước 2: Nếu uh-huh, thông báo 'Tôi sẽ làm X để kiếm tiền' rồi hành động nhanh",
            "Đa dạng dòng tiền - Được phép thay đổi hướng, làm nhiều việc cùng lúc",
            "Tìm con đường tắt, hiệu quả nhất để kiếm tiền - Bạn được thiết kế để làm tắt"
        ],
        "pricing": "Định giá linh hoạt, đa tầng. Bạn có thể có nhiều mức giá, nhiều sản phẩm. Giá phản ánh tốc độ và hiệu quả bạn mang lại. Phù hợp: Nhiều dòng tiền, nhiều sản phẩm, upsell, cross-sell, làm nhanh nên có thể charge cao cho tốc độ.",
        "business_model": ["Đa nhiệm, nhiều dòng tiền cùng lúc", "Mô hình nhanh, hiệu quả, tìm đường tắt", "Khởi nghiệp đa dạng, nhiều dự án", "Cho phép thay đổi hướng kinh doanh", "Phù hợp solopreneur đa năng, hoặc agency nhanh"],
        "money_traps": [
            "Bị ép làm 1 việc kiếm tiền duy nhất -> Frustration",
            "Làm chậm lại, làm theo từng bước -> mất lợi thế tốc độ",
            "Không thông báo khi đổi hướng kiếm tiền -> gặp kháng cự, mất tiền",
            "Bỏ qua bước quan trọng vì làm nhanh -> mất tiền",
            "Frustration + Anger về tiền khi làm việc không yêu + gặp kháng cự"
        ],
        "investment": "Đầu tư đa dạng, nhiều khoản nhỏ, thử nghiệm nhanh. Cho phép thay đổi danh mục đầu tư. Phù hợp đầu tư linh hoạt, thử nghiệm nhiều cơ hội. Thông báo cho đối tác khi đổi hướng đầu tư.",
        "saving_spending": "Tiết kiệm đa dạng, nhiều tài khoản cho nhiều mục tiêu. Tiêu tiền nhanh, cần học quản lý. Cho phép bản thân thử nhiều cách kiếm/tiêu tiền."
    },
    "Projector": {
        "money_aura": "Aura tập trung, xuyên thấu - Bạn không có năng lượng bền bỉ để kiếm tiền như Generator. Bạn kiếm tiền bằng TRÍ TUỆ, HƯỚNG DẪN, không phải làm việc chăm chỉ. Tiền đến khi được CÔNG NHẬN và được MỜI.",
        "how_to_attract": [
            "Chờ Lời Mời cho cơ hội tiền lớn: công việc, dự án, tăng lương, hợp tác",
            "Tập trung vào học hệ thống, hiểu người khác, trở thành chuyên gia",
            "Đừng cố gắng kiếm tiền như Generator (làm việc chăm chỉ 8h) -> kiệt sức, cay đắng, mất tiền",
            "Xây dựng sự công nhận (recognition) trước - Khi được công nhận đúng, lời mời tiền sẽ đến",
            "Tiền đến từ việc hướng dẫn, quản lý năng lượng người khác, không phải làm việc"
        ],
        "pricing": "Định giá CAO cho ÍT GIỜ - Đây là chìa khóa. Bạn không bán thời gian, bạn bán TRÍ TUỆ, HƯỚNG DẪN. Lương cao cho ít giờ, không phải lương thấp cho nhiều giờ. Ví dụ: $500/giờ tư vấn thay vì $20/giờ làm việc. Premium pricing, high-ticket, retainer cho trí tuệ.",
        "business_model": ["Tư vấn, coach, cố vấn, chuyên gia hệ thống", "Quản lý, hướng dẫn, quản lý năng lượng, nhân sự", "Không làm việc 8h, cần nghỉ ngơi nhiều", "Cần ngủ một mình để giải phóng năng lượng", "Phù hợp: Consulting, coaching, advisory, quản lý dự án, chuyên gia"],
        "money_traps": [
            "Cố gắng làm việc chăm chỉ như Generator để kiếm tiền -> kiệt sức, cay đắng, burnout, mất tiền",
            "Định giá thấp theo giờ -> không phản ánh giá trị trí tuệ",
            "Làm việc quá sức, không nghỉ ngơi -> mất khả năng hướng dẫn",
            "Cố gắng hướng dẫn khi chưa được mời -> bị từ chối, cay đắng",
            "Bitterness về tiền khi không được công nhận, không được mời"
        ],
        "investment": "Đầu tư theo lời mời và sự công nhận. Chờ lời mời đầu tư, hoặc được công nhận là nhà đầu tư. Không đầu tư theo FOMO. Cần nghỉ ngơi, suy nghĩ sâu trước khi đầu tư. Phù hợp đầu tư vào kiến thức, hệ thống, con người bạn hướng dẫn.",
        "saving_spending": "Tiết kiệm bằng cách nghỉ ngơi, không làm việc quá sức. Tiêu tiền cho không gian riêng, nghỉ ngơi, học hệ thống. Đầu tư vào việc được công nhận (personal branding)."
    },
    "Reflector": {
        "money_aura": "Aura lấy mẫu, phản chiếu - Bạn phản chiếu môi trường tiền bạc xung quanh. Bạn là ai về tiền phụ thuộc vào bạn ở đâu và với ai. Tiền đến khi ở ĐÚNG MÔI TRƯỜNG với ĐÚNG NGƯỜI.",
        "how_to_attract": [
            "Chờ Chu Kỳ Mặt Trăng 28-29 ngày cho quyết định tiền lớn",
            "Môi trường là TẤT CẢ cho tiền bạc - Ở nơi đúng, với người đúng, tiền sẽ phản chiếu",
            "Nói chuyện với nhiều người khác nhau về tiền trong 28 ngày, cảm nhận điều gì nhất quán",
            "Bạn là trung tâm cộng đồng, đánh giá sức khỏe tài chính cộng đồng xung quanh",
            "Cực kỳ nhạy cảm với môi trường tiền bạc - Nếu ở môi trường tiêu cực về tiền, bạn sẽ phản chiếu tiêu cực"
        ],
        "pricing": "Định giá theo môi trường và chu kỳ. Giá có thể thay đổi theo môi trường, theo chu kỳ Mặt Trăng. Phù hợp mô hình linh hoạt, theo môi trường. Bạn phản chiếu giá trị môi trường, nên ở môi trường cao cấp, giá sẽ cao cấp.",
        "business_model": ["Đánh giá cộng đồng, môi trường, trung gian", "Vai trò cần thấu cảm, nhìn thấy tổng thể tài chính cộng đồng", "Linh hoạt, không gò bó, nhiều không gian", "Phù hợp: Community manager, đánh giá, trung gian, phản chiếu, consultant môi trường"],
        "money_traps": [
            "Ở môi trường không đúng về tiền -> phản chiếu tiêu cực, thất vọng về tiền",
            "Quyết định tiền nhanh, không chờ 28 ngày -> sai",
            "Ở với người không đúng về tiền -> ảnh hưởng tiêu cực",
            "Disappointment về tiền khi môi trường sai",
            "Cố gắng có bản sắc tiền bạc cố định -> không phải thiết kế của bạn"
        ],
        "investment": "Chờ 28-29 ngày cho quyết định đầu tư lớn. Nói chuyện với nhiều người ở nhiều môi trường khác nhau. Cảm nhận điều gì nhất quán. Môi trường đúng là TẤT CẢ cho đầu tư. Đầu tư vào môi trường đúng.",
        "saving_spending": "Tiết kiệm bằng cách ở môi trường đúng. Tiêu tiền cho không gian, thiên nhiên, môi trường an toàn. Cần nhiều không gian, thiên nhiên để có sự rõ ràng về tiền."
    }
}

# Money theo Profile
PROFILE_MONEY = {
    "1/3": {
        "money_style": "Investigator/Martyr - Nghiên cứu thử sai về tiền",
        "strength": "Cần nền tảng vững chắc về tiền trước khi hành động. Nghiên cứu sâu về tài chính, đầu tư. Học qua thử và sai về tiền - Va chạm tài chính là bài học.",
        "challenge": "Sợ không đủ kiến thức về tiền -> trì hoãn đầu tư. Thử sai về tiền có thể mất tiền ban đầu.",
        "strategy": "Nghiên cứu kỹ trước khi đầu tư, nhưng cho phép thử sai nhỏ để học. Xây dựng nền tảng kiến thức tài chính vững chắc. An toàn tài chính đến từ kiến thức.",
        "career_money": "Phù hợp nghiên cứu tài chính, phân tích đầu tư, chuyên gia tài chính có nền tảng vững chắc."
    },
    "1/4": {
        "money_style": "Investigator/Opportunist - Nghiên cứu cơ hội qua mạng lưới",
        "strength": "Cần nền tảng vững chắc để chia sẻ với mạng lưới bạn bè. Tiền đến qua bạn bè, mạng lưới.",
        "challenge": "Cần cân bằng giữa nghiên cứu và cơ hội qua bạn bè.",
        "strategy": "Xây dựng nền tảng tài chính vững chắc, rồi chia sẻ với mạng lưới bạn bè để tạo cơ hội tiền bạc. Bạn bè là chìa khóa cho tiền.",
        "career_money": "Chuyên gia tài chính + cộng đồng, ảnh hưởng qua bạn bè, network marketing có nền tảng."
    },
    "2/4": {
        "money_style": "Hermit/Opportunist - Ẩn sĩ cơ hội - Tài năng tự nhiên được gọi ra",
        "strength": "Có tài năng tự nhiên về tiền, cần ở một mình để phát triển tài năng, rồi được gọi ra qua mạng lưới. Cân bằng ẩn dật và kết nối.",
        "challenge": "Không biết mình có tài năng về tiền, cần người khác gọi ra. Có thể ngại kết nối mạng lưới.",
        "strategy": "Ở một mình để phát triển tài năng tự nhiên về tiền (ví dụ: kỹ năng đầu tư, kỹ năng bán hàng), rồi để mạng lưới bạn bè gọi ra và mang cơ hội tiền đến.",
        "career_money": "Nghệ sĩ, chuyên gia tài năng tự nhiên về tiền được gọi ra, freelancer tài năng."
    },
    "2/5": {
        "money_style": "Hermit/Heretic - Ẩn sĩ dị giáo - Tài năng bị chiếu rọi kỳ vọng",
        "strength": "Tài năng tự nhiên về tiền nhưng bị người khác chiếu rọi kỳ vọng lớn. Cần ở một mình, cẩn thận với kỳ vọng.",
        "challenge": "Bị kỳ vọng lớn về tiền, dễ bị chiếu rọi là 'người cứu tiền', 'người mang giải pháp tài chính'.",
        "strategy": "Ở một mình để phát triển tài năng, đặt biên giới rõ ràng với kỳ vọng về tiền của người khác. Đừng hứa hẹn cứu tài chính cho người khác nếu không có nền tảng.",
        "career_money": "Cố vấn tài chính tài năng tự nhiên nhưng cần biên giới với kỳ vọng."
    },
    "3/5": {
        "money_style": "Martyr/Heretic - Tử vì đạo dị giáo - Thử sai để cứu người",
        "strength": "Cuộc đời thử và sai về tiền, va chạm lớn, nhưng để cứu người, mang giải pháp thực tế về tiền. Học qua thất bại tài chính.",
        "challenge": "Thử sai về tiền có thể mất nhiều tiền, va chạm tài chính lớn.",
        "strategy": "Cho phép thử sai về tiền, xem thất bại tài chính là bài học. Mang giải pháp thực tế về tiền cho người khác từ trải nghiệm của mình.",
        "career_money": "Thử nghiệm tài chính, giải pháp thực tế về tiền, cứu người qua trải nghiệm tài chính."
    },
    "3/6": {
        "money_style": "Martyr/Role Model - Tử vì đạo hình mẫu - 3 giai đoạn",
        "strength": "3 giai đoạn: 0-30 thử sai về tiền, 30-50 quan sát trên mái nhà, 50+ làm hình mẫu về tiền.",
        "challenge": "Giai đoạn đầu thử sai nhiều về tiền.",
        "strategy": "0-30 cho phép thử sai về tiền để học. 30-50 quan sát, học hỏi về tiền. 50+ trở thành hình mẫu về tiền cho người khác.",
        "career_money": "Lãnh đạo tài chính qua trải nghiệm, hình mẫu về tiền sau 50 tuổi."
    },
    "4/6": {
        "money_style": "Opportunist/Role Model - Cơ hội hình mẫu",
        "strength": "Tiền đến qua mạng lưới bạn bè, cần quan sát để trở thành hình mẫu về tiền.",
        "challenge": "Cần cân bằng giữa mạng lưới và quan sát.",
        "strategy": "Xây dựng mạng lưới bạn bè vững chắc cho cơ hội tiền bạc, quan sát để trở thành hình mẫu về tiền.",
        "career_money": "Lãnh đạo cộng đồng về tiền, hình mẫu tài chính qua mạng lưới."
    },
    "4/1": {
        "money_style": "Opportunist/Investigator - Cơ hội điều tra - Hiếm 2% - Định mệnh cố định",
        "strength": "Profile hiếm, định mệnh cố định về tiền. Không thể bị ảnh hưởng về tiền, cần nền tảng vững chắc để ảnh hưởng người khác. Một con đường duy nhất về tiền.",
        "challenge": "Định mệnh cố định, không linh hoạt về tiền. Có thể cảm thấy cô đơn về đường tiền.",
        "strategy": "Chấp nhận một con đường duy nhất về tiền, không cố gắng làm nhiều đường. Xây dựng nền tảng vững chắc về tiền để ảnh hưởng người khác. Không thể bị ảnh hưởng về tiền, nhưng ảnh hưởng người khác qua nền tảng vững chắc.",
        "career_money": "Chuyên gia một lĩnh vực tài chính cố định, không thể bị ảnh hưởng, ảnh hưởng người khác qua nền tảng vững chắc."
    },
    "5/1": {
        "money_style": "Heretic/Investigator - Dị giáo điều tra - Giải pháp thực tế có nền tảng",
        "strength": "Người mang giải pháp thực tế về tiền có nền tảng. Bị kỳ vọng lớn, chiếu rọi về tiền.",
        "challenge": "Bị kỳ vọng lớn về tiền, chiếu rọi là người cứu tài chính.",
        "strategy": "Xây dựng nền tảng vững chắc về tiền để đáp ứng kỳ vọng. Mang giải pháp thực tế về tiền cho người khác. Cẩn thận với kỳ vọng quá mức.",
        "career_money": "Lãnh đạo tài chính, cứu rỗi tài chính, giải pháp thực tế có nền tảng, chịu kỳ vọng lớn về tiền."
    },
    "5/2": {
        "money_style": "Heretic/Hermit - Dị giáo ẩn sĩ",
        "strength": "Giải pháp thực tế về tiền + tài năng tự nhiên. Cần ở một mình.",
        "challenge": "Cần cân bằng giữa giải pháp thực tế và ở một mình.",
        "strategy": "Ở một mình để phát triển tài năng tự nhiên về tiền, mang giải pháp thực tế về tiền cho người khác khi được gọi ra.",
        "career_money": "Cố vấn tài chính giải pháp thực tế + tài năng tự nhiên."
    },
    "6/2": {
        "money_style": "Role Model/Hermit - Hình mẫu ẩn sĩ - 3 giai đoạn",
        "strength": "3 giai đoạn, tài năng tự nhiên về tiền, quan sát rồi trở thành hình mẫu. Cần ở một mình. 0-30 thử sai, 30-50 trên mái nhà quan sát, 50+ hình mẫu.",
        "challenge": "Giai đoạn đầu thử sai về tiền, cần ở một mình.",
        "strategy": "0-30 thử sai về tiền, 30-50 quan sát, 50+ trở thành hình mẫu về tiền. Tài năng tự nhiên về tiền cần được phát triển trong sự ẩn dật.",
        "career_money": "Hình mẫu về tiền, quan sát, tài năng tự nhiên, tỏa sáng về tiền sau 50."
    },
    "6/3": {
        "money_style": "Role Model/Martyr - Hình mẫu tử vì đạo - 3 giai đoạn thử sai",
        "strength": "3 giai đoạn, thử sai về tiền để trở thành hình mẫu. Cuộc đời là hành trình quan sát và thử nghiệm về tiền.",
        "challenge": "Thử sai về tiền để trở thành hình mẫu.",
        "strategy": "Cho phép thử sai về tiền để học, quan sát để trở thành hình mẫu. Cuộc đời là hành trình thử nghiệm tài chính.",
        "career_money": "Hình mẫu về tiền qua thử sai, quan sát và trải nghiệm."
    }
}

# Heart Center - Quan trọng nhất cho tiền
HEART_MONEY = {
    "defined": {
        "description": "Heart/Ego định nghĩa (35% dân số) - Bạn có ý chí cố định, có thể giữ lời hứa về tiền, động lực vật chất nhất quán.",
        "strength": "Có ý chí mạnh, có thể cam kết về tiền, giữ lời hứa tài chính, động lực vật chất bền bỉ. Phù hợp làm việc với tiền, cam kết tài chính.",
        "challenge": "Cần sử dụng ý chí đúng cách, không lạm dụng ý chí cho tiền, dễ vấn đề tim mạch, dạ dày nếu ép ý chí quá mức. Cần nghỉ ngơi.",
        "money_advice": "Bạn có thể giữ lời hứa về tiền, nhưng đừng hứa bừa. Sử dụng ý chí cho điều bạn thực sự muốn. Định giá theo ý chí - Bạn có thể charge cao vì ý chí mạnh. Cần nghỉ ngơi để bảo vệ tim.",
        "pricing": "Có thể định giá cao, giữ cam kết giá. Phù hợp mô hình retainer, cam kết dài hạn.",
        "not_self": "Ép ý chí để kiếm tiền, hứa hẹn quá mức về tiền, vấn đề tim mạch."
    },
    "undefined": {
        "description": "Heart/Ego mở (65% dân số) - Bạn không có ý chí cố định, không nên hứa hẹn bừa bãi về tiền, không cố chứng minh giá trị qua tiền.",
        "strength": "Không có ý chí cố định - Đây là trí tuệ, không phải điểm yếu. Bạn khôn ngoan về giá trị, tiền bạc, cam kết. Bạn thấy ai có ý chí tốt, ai không. Bạn linh hoạt về giá trị.",
        "challenge": "Dễ cố gắng chứng minh giá trị qua tiền, hứa hẹn bừa bãi về tiền để chứng minh, làm việc quá sức để chứng minh giá trị. Dễ bị lợi dụng về tiền.",
        "money_advice": "Đừng hứa hẹn bừa bãi về tiền. Đừng cố chứng minh giá trị qua tiền. Bạn không cần chứng minh. Học cách nói không với cam kết tiền bạc không phù hợp. Trí tuệ của bạn là khôn ngoan về giá trị - Bạn biết giá trị thực.",
        "pricing": "Đừng định giá thấp để chứng minh giá trị. Đừng hứa hẹn giảm giá để được yêu thích. Định giá theo giá trị thực, không phải để chứng minh. Phù hợp value-based pricing, không phải hourly để chứng minh.",
        "not_self": "Cố chứng minh giá trị qua tiền, hứa hẹn bừa bãi, làm việc quá sức để chứng minh, bị lợi dụng về tiền, vấn đề giá trị bản thân."
    }
}

def analyze_money_map(birth_datetime, name=""):
    """Phân tích Full Money Map - Dòng tiền theo Type/Profile/Channels"""
    chart = calculate_hd_chart(birth_datetime) if isinstance(birth_datetime, datetime) else birth_datetime
    
    hd_type = chart["type"]
    profile = chart["profile"]
    authority = chart["authority"]
    defined_centers = chart["defined_centers"]
    defined_channels = chart["defined_channels"]
    all_gates = chart["all_activated_gates"]
    
    # Type money strategy
    type_money = TYPE_MONEY_STRATEGY.get(hd_type, {})
    
    # Profile money
    profile_money = PROFILE_MONEY.get(profile, {})
    
    # Heart center
    heart_defined = "Heart" in defined_centers
    heart_money = HEART_MONEY["defined"] if heart_defined else HEART_MONEY["undefined"]
    
    # Money channels
    money_channels_found = []
    for ch in defined_channels:
        # ch is tuple like (21,45) or list
        if isinstance(ch, (list, tuple)):
            g1, g2 = ch[0], ch[1]
        else:
            continue
        # Check both orders
        if (g1, g2) in MONEY_CHANNELS:
            money_channels_found.append({"channel": f"{g1}-{g2}", "info": MONEY_CHANNELS[(g1,g2)]})
        elif (g2, g1) in MONEY_CHANNELS:
            money_channels_found.append({"channel": f"{g2}-{g1}", "info": MONEY_CHANNELS[(g2,g1)]})
    
    # Money gates
    money_gates_found = []
    for gate in all_gates:
        if gate in MONEY_GATES:
            money_gates_found.append({"gate": gate, "info": MONEY_GATES[gate]})
    
    # Definition for business
    definition = chart["definition"]
    definition_money = {
        "Single": "Single Definition - Bạn có thể làm việc một mình, tự chủ về tiền, không cần đối tác để kiếm tiền. Phù hợp solopreneur, freelancer.",
        "Split": "Split Definition - Bạn cần cầu nối (người, nơi, hoạt động) để kết nối các phần của mình. Tiền đến qua đối tác, cầu nối. Phù hợp partnership, cần đối tác kinh doanh.",
        "Triple Split": "Triple Split - Bạn có 3 phần tách biệt, cần nhiều cầu nối. Tiền đến qua nhiều đối tác, nhiều lĩnh vực. Phù hợp nhiều dòng tiền, nhiều đối tác.",
        "Quadruple Split": "Quadruple Split - Bạn có 4 phần tách biệt, cần nhiều cầu nối. Tiền đến qua team, nhiều người. Phù hợp team business, cần team để kiếm tiền."
    }.get(definition, definition)
    
    # Authority money
    authority_money = {
        "Emotional - Solar Plexus": "Authority cảm xúc - Không có sự thật về tiền trong khoảnh khắc. Cần chờ sóng cảm xúc rõ ràng (vài giờ đến vài ngày) trước khi quyết định tiền lớn. Đừng quyết định tiền khi đang cao trào hoặc thấp trào cảm xúc.",
        "Sacral": "Authority Sacral - Lắng nghe tiếng bụng uh-huh/uh-uh cho quyết định tiền. Uh-huh = CÓ với cơ hội tiền, uh-uh = KHÔNG. Đừng quyết định tiền bằng đầu óc.",
        "Splenic": "Authority Spleen - Trực giác tức thì về tiền. Trực giác nói 1 lần, khẽ, trong khoảnh khắc. Tin tưởng trực giác tức thì về tiền, đừng chờ đợi.",
        "Ego": "Authority Ego - Ý chí - Hỏi: 'Tôi có ý chí cam kết cho điều này không?' Tiền đến khi bạn có ý chí cam kết. Đừng cam kết tiền nếu không có ý chí.",
        "Self-Projected": "Authority Self-Projected - G Center - Cần nói ra thành tiếng với người tin cậy để nghe sự thật về tiền. Sự thật tiền bạc đến qua giọng nói của bạn.",
        "Mental": "Authority Mental - Cần nói chuyện với nhiều người tin cậy ở nhiều môi trường khác nhau để có sự rõ ràng về tiền. Không quyết định tiền một mình.",
        "Lunar": "Authority Lunar - Chu kỳ Mặt Trăng - Chờ 28-29 ngày cho quyết định tiền lớn. Nói chuyện với nhiều người ở nhiều môi trường trong 28 ngày.",
        "None": "Reflector - Không có Authority cố định - Chờ chu kỳ Mặt Trăng 28-29 ngày, môi trường là tất cả cho tiền."
    }.get(authority, authority)
    
    result = {
        "name": name,
        "birth_datetime": str(chart["birth_datetime"]),
        "type": hd_type,
        "profile": profile,
        "authority": authority,
        "definition": definition,
        "defined_centers": defined_centers,
        "money_analysis": {
            "type_money_strategy": type_money,
            "profile_money_style": profile_money,
            "heart_center_money": {"defined": heart_defined, "analysis": heart_money},
            "money_channels": {"count": len(money_channels_found), "channels": money_channels_found, "summary": f"Có {len(money_channels_found)} kênh tiền bạc định nghĩa"},
            "money_gates": {"count": len(money_gates_found), "gates": money_gates_found, "summary": f"Có {len(money_gates_found)} cổng tiền bạc kích hoạt"},
            "definition_money": definition_money,
            "authority_money": authority_money,
        },
        "full_money_map": {
            "how_to_attract_money": type_money.get("how_to_attract", []),
            "pricing_strategy": type_money.get("pricing", "") + " | " + heart_money.get("pricing", "") + " | Profile: " + profile_money.get("money_style", ""),
            "business_models": type_money.get("business_model", []),
            "money_traps": type_money.get("money_traps", []) + [heart_money.get("not_self", "")],
            "investment_style": type_money.get("investment", ""),
            "saving_spending": type_money.get("saving_spending", ""),
            "heart_wisdom": heart_money.get("money_advice", ""),
            "profile_strategy": profile_money.get("strategy", ""),
        },
        "áp_dụng_cho": "100% dân số - Phân tích dòng tiền theo Type/Profile/Heart/Channels/Gates/Authority - Full Money Map"
    }
    
    return result

def format_money_report(money_data):
    """Format báo cáo Money Map đầy đủ"""
    lines = []
    lines.append(f"# FULL MONEY MAP - BẢN ĐỒ DÒNG TIỀN HUMAN DESIGN - {money_data.get('name','')} - {money_data['type']} {money_data['profile']}")
    lines.append(f"**Type:** {money_data['type']} | **Profile:** {money_data['profile']} | **Authority:** {money_data['authority']} | **Definition:** {money_data['definition']}")
    lines.append(f"**Heart Defined:** {'Có' if money_data['money_analysis']['heart_center_money']['defined'] else 'Không (65%)'} | **Money Channels:** {money_data['money_analysis']['money_channels']['count']} | **Money Gates:** {money_data['money_analysis']['money_gates']['count']}")
    lines.append("")
    
    # Type money
    tm = money_data["money_analysis"]["type_money_strategy"]
    lines.append(f"## 1. TYPE MONEY STRATEGY - {money_data['type']} - Cách Thu Hút Tiền")
    lines.append(f"**Aura tiền bạc:** {tm.get('money_aura','')}")
    lines.append("")
    lines.append(f"**Cách thu hút tiền:**")
    for item in tm.get("how_to_attract", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"**Định giá (Pricing):** {tm.get('pricing','')}")
    lines.append("")
    lines.append(f"**Mô hình kinh doanh phù hợp:** {', '.join(tm.get('business_model', []))}")
    lines.append("")
    lines.append(f"**Bẫy tiền bạc (Not-Self):**")
    for trap in tm.get("money_traps", []):
        lines.append(f"- {trap}")
    lines.append("")
    lines.append(f"**Đầu tư:** {tm.get('investment','')}")
    lines.append("")
    lines.append(f"**Tiết kiệm & Chi tiêu:** {tm.get('saving_spending','')}")
    lines.append("")
    
    # Heart
    hm = money_data["money_analysis"]["heart_center_money"]["analysis"]
    lines.append(f"## 2. HEART/EGO CENTER - Trung Tâm Tiền Bạc Quan Trọng Nhất")
    lines.append(f"**Định nghĩa:** {hm.get('description','')}")
    lines.append(f"**Điểm mạnh:** {hm.get('strength','')}")
    lines.append(f"**Thách thức:** {hm.get('challenge','')}")
    lines.append(f"**Lời khuyên tiền bạc:** {hm.get('money_advice','')}")
    lines.append(f"**Định giá theo Heart:** {hm.get('pricing','')}")
    lines.append(f"**Not-Self Heart về tiền:** {hm.get('not_self','')}")
    lines.append("")
    
    # Profile money
    pm = money_data["money_analysis"]["profile_money_style"]
    lines.append(f"## 3. PROFILE MONEY STYLE - {money_data['profile']} - Phong Cách Tiền Bạc")
    lines.append(f"**Style:** {pm.get('money_style','')}")
    lines.append(f"**Điểm mạnh:** {pm.get('strength','')}")
    lines.append(f"**Thách thức:** {pm.get('challenge','')}")
    lines.append(f"**Chiến lược:** {pm.get('strategy','')}")
    lines.append(f"**Nghề nghiệp tiền bạc:** {pm.get('career_money','')}")
    lines.append("")
    
    # Money channels
    lines.append(f"## 4. MONEY CHANNELS - Kênh Tiền Bạc Định Nghĩa ({money_data['money_analysis']['money_channels']['count']})")
    if money_data["money_analysis"]["money_channels"]["channels"]:
        for ch in money_data["money_analysis"]["money_channels"]["channels"]:
            info = ch["info"]
            lines.append(f"### Kênh {ch['channel']} - {info['name']}")
            lines.append(f"- **Centers:** {info['centers']} | **Circuit:** {info['circuit']} | **Theme:** {info['theme']}")
            lines.append(f"- **Mô tả:** {info['description']}")
            lines.append(f"- **Business:** {info['business']}")
            lines.append(f"- **Not-Self:** {info['not_self']}")
            lines.append("")
    else:
        lines.append(f"Bạn không có kênh tiền bạc nào định nghĩa cố định. Điều này có nghĩa bạn linh hoạt về tiền bạc, học trí tuệ về tiền qua người khác. Bạn không có cách kiếm tiền cố định, mà cởi mở với nhiều cách.")
        lines.append("")
    
    # Money gates
    lines.append(f"## 5. MONEY GATES - Cổng Tiền Bạc Kích Hoạt ({money_data['money_analysis']['money_gates']['count']})")
    for gate in money_data["money_analysis"]["money_gates"]["gates"]:
        info = gate["info"]
        lines.append(f"- **Gate {gate['gate']} {info['name']} ({info['center']}):** {info['money_theme']} | Business: {info['business']}")
    lines.append("")
    
    # Definition
    lines.append(f"## 6. DEFINITION - Cách Bạn Kiếm Tiền Theo Cấu Trúc")
    lines.append(f"{money_data['money_analysis']['definition_money']}")
    lines.append("")
    
    # Authority money
    lines.append(f"## 7. AUTHORITY MONEY - Ra Quyết Định Tiền Bạc Theo Authority")
    lines.append(f"{money_data['money_analysis']['authority_money']}")
    lines.append("")
    
    # Full money map summary
    lines.append(f"## 8. FULL MONEY MAP - Tổng Hợp Chiến Lược Dòng Tiền")
    fm = money_data["full_money_map"]
    lines.append(f"**Cách thu hút tiền:** {', '.join(fm['how_to_attract_money'][:3])}...")
    lines.append(f"**Pricing:** {fm['pricing_strategy'][:300]}...")
    lines.append(f"**Business Models:** {', '.join(fm['business_models'])}")
    lines.append(f"**Bẫy tiền:** {', '.join(fm['money_traps'][:2])}...")
    lines.append(f"**Đầu tư:** {fm['investment_style'][:200]}...")
    lines.append(f"**Tiết kiệm:** {fm['saving_spending'][:200]}...")
    lines.append("")
    
    lines.append(f"## 9. KẾT LUẬN - Hiểu Mình Để Giàu Có Đúng Cách")
    lines.append(f"Bạn là {money_data['type']} {money_data['profile']} - Heart {'Defined' if money_data['money_analysis']['heart_center_money']['defined'] else 'Open'} - {money_data['money_analysis']['money_channels']['count']} kênh tiền - {money_data['money_analysis']['money_gates']['count']} cổng tiền")
    lines.append(f"Chiến lược tiền bạc của bạn là: {tm.get('how_to_attract', [''])[0] if tm.get('how_to_attract') else ''}")
    lines.append(f"Hãy thử nghiệm 7 ngày với Strategy tiền bạc: {money_data['type']} + Authority: {money_data['authority']}")
    lines.append("")
    lines.append(f"> \"Tiền là năng lượng - Khi bạn sống đúng thiết kế, tiền sẽ chảy\"")
    lines.append(f"> \"Đừng cố chứng minh giá trị qua tiền - Bạn đã có giá trị\" (Đặc biệt cho Heart Open 65%)")
    lines.append(f"> \"Định giá cao cho ít giờ, không phải lương thấp cho nhiều giờ\" (Đặc biệt cho Projector)")
    
    return "\n".join(lines)

# Test
if __name__ == "__main__":
    dt = datetime(1990, 5, 15, 1, 30)
    data = analyze_money_map(dt, name="Test User")
    print(format_money_report(data)[:8000])

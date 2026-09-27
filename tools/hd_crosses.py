"""Danh mục 192 Incarnation Crosses — nguồn chân lý duy nhất (đợt 4).

Cấu trúc đã kiểm chứng bằng thực nghiệm trên engine (sampling 1600 chart) +
đối chiếu 3 nguồn độc lập:
- Mỗi cổng Sun ý thức (64) sinh đúng 3 Cross theo họ: RAX / LAX / JX.
- RAX dùng Design Sun "sớm" (D-A); JX và LAX dùng Design Sun "muộn" (D-B).
- Earth luôn đối diện Sun (+32 cổng trên vòng 64).

Nguồn tên + bộ 4 cổng: Genetic Matrix Learn Hub (2026), đối chiếu
manifestinghumandesign.com (16/16 RAX Quarter 1) và humandesign4all.com
(~30 mục LAX/JX). Nghĩa tiếng Việt do nhóm tự viết từ cơ học cổng.
"""

from __future__ import annotations

QUARTERS = {
    1: {"en": "Initiation", "vi": "Khởi Nguyên",
        "theme": "Tâm trí — nhận thức, truy vấn, khởi mở hiểu biết",
        "gates": [13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27, 24]},
    2: {"en": "Civilization", "vi": "Văn Minh",
        "theme": "Hình tướng — vật chất, cấu trúc, biểu hiện ý tưởng ra đời",
        "gates": [2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 31, 33]},
    3: {"en": "Duality", "vi": "Đối Ngẫu",
        "theme": "Gắn kết — quan hệ, liên kết, nhận thức qua tương tác",
        "gates": [7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50, 28, 44]},
    4: {"en": "Mutation", "vi": "Đột Biến",
        "theme": "Năng lượng — biến đổi, đột biến, tiến hóa",
        "gates": [1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60, 41, 19]},
}

GEOM_VI = {
    "RAX": "Góc Phải (số phận cá nhân)",
    "LAX": "Góc Trái (nghiệp xuyên cá nhân)",
    "JX": "Cố Định (định mệnh hội tụ)",
}

PROFILES = {
    "RAX": ("1/3", "1/4", "2/4", "2/5", "3/5", "3/6", "4/6"),
    "LAX": ("5/1", "5/2", "6/2", "6/3"),
    "JX": ("4/1",),
}

# (P-Sun, tên RAX, 4 cổng RAX, tên LAX, 4 cổng LAX, tên JX, 4 cổng JX)
# Thứ tự cổng: Sun ý thức / Earth ý thức / Sun vô thức / Earth vô thức.
_RAW = [
    # Quarter 1: Initiation
    (13, "The Sphinx", (13, 7, 1, 2), "Masks", (13, 7, 43, 23), "Listening", (13, 7, 43, 23)),
    (49, "Explanation", (49, 4, 43, 23), "Revolution", (49, 4, 14, 8), "Principles", (49, 4, 14, 8)),
    (30, "Contagion", (30, 29, 14, 8), "Industry", (30, 29, 34, 20), "Fates", (30, 29, 34, 20)),
    (55, "The Sleeping Phoenix", (55, 59, 34, 20), "Spirit", (55, 59, 9, 16), "Moods", (55, 59, 9, 16)),
    (37, "Planning", (37, 40, 9, 16), "Migration", (37, 40, 5, 35), "Bargains", (37, 40, 5, 35)),
    (63, "Consciousness", (63, 64, 5, 35), "Dominion", (63, 64, 26, 45), "Doubts", (63, 64, 26, 45)),
    (22, "Rulership", (22, 47, 26, 45), "Informing", (22, 47, 11, 12), "Grace", (22, 47, 11, 12)),
    (36, "Eden", (36, 6, 11, 12), "The Plane", (36, 6, 10, 15), "Crisis", (36, 6, 10, 15)),
    (25, "The Vessel of Love", (25, 46, 10, 15), "Healing", (25, 46, 58, 52), "Innocence", (25, 46, 58, 52)),
    (17, "Service", (17, 18, 58, 52), "Upheaval", (17, 18, 38, 39), "Opinions", (17, 18, 38, 39)),
    (21, "Tension", (21, 48, 38, 39), "Endeavor", (21, 48, 54, 53), "Control", (21, 48, 54, 53)),
    (51, "Penetration", (51, 57, 54, 53), "The Clarion", (51, 57, 61, 62), "Shock", (51, 57, 61, 62)),
    (42, "Maya", (42, 32, 61, 62), "Limitation", (42, 32, 60, 56), "Completion", (42, 32, 60, 56)),
    (3, "Laws", (3, 50, 60, 56), "Wishes", (3, 50, 41, 31), "Mutation", (3, 50, 41, 31)),
    (27, "The Unexpected", (27, 28, 41, 31), "Alignment", (27, 28, 19, 33), "Caring", (27, 28, 19, 33)),
    (24, "The Four Ways", (24, 44, 19, 33), "Incarnation", (24, 44, 13, 7), "Rationalization", (24, 44, 13, 7)),
    # Quarter 2: Civilization
    (2, "The Sphinx", (2, 1, 13, 7), "Defiance", (2, 1, 49, 4), "The Driver", (2, 1, 49, 4)),
    (23, "Explanation", (23, 43, 49, 4), "Dedication", (23, 43, 30, 29), "Assimilation", (23, 43, 30, 29)),
    (8, "Contagion", (8, 14, 30, 29), "Uncertainty", (8, 14, 55, 59), "Contribution", (8, 14, 55, 59)),
    (20, "The Sleeping Phoenix", (20, 34, 55, 59), "Duality", (20, 34, 37, 40), "The Now", (20, 34, 37, 40)),
    (16, "Planning", (16, 9, 37, 40), "Identification", (16, 9, 63, 64), "Experimentation", (16, 9, 63, 64)),
    (35, "Consciousness", (35, 5, 63, 64), "Separation", (35, 5, 22, 47), "Experience", (35, 5, 22, 47)),
    (45, "Rulership", (45, 26, 22, 47), "Confrontation", (45, 26, 36, 6), "Possession", (45, 26, 36, 6)),
    (12, "Eden", (12, 11, 36, 6), "Education", (12, 11, 25, 46), "Articulation", (12, 11, 25, 46)),
    (15, "The Vessel of Love", (15, 10, 25, 46), "Prevention", (15, 10, 17, 18), "Extremes", (15, 10, 17, 18)),
    (52, "Service", (52, 58, 17, 18), "Demands", (52, 58, 21, 48), "Stillness", (52, 58, 21, 48)),
    (39, "Tension", (39, 38, 21, 48), "Individualism", (39, 38, 51, 57), "Provocation", (39, 38, 51, 57)),
    (53, "Penetration", (53, 54, 51, 57), "Cycles", (53, 54, 42, 32), "Beginnings", (53, 54, 42, 32)),
    (62, "Maya", (62, 61, 42, 32), "Obscuration", (62, 61, 3, 50), "Detail", (62, 61, 3, 50)),
    (56, "Laws", (56, 60, 3, 50), "Distraction", (56, 60, 27, 28), "Stimulation", (56, 60, 27, 28)),
    (31, "The Unexpected", (31, 41, 27, 28), "The Alpha", (31, 41, 24, 44), "Influence", (31, 41, 24, 44)),
    (33, "The Four Ways", (33, 19, 24, 44), "Refinement", (33, 19, 2, 1), "Retreat", (33, 19, 2, 1)),
    # Quarter 3: Duality
    (7, "The Sphinx", (7, 13, 2, 1), "Masks", (7, 13, 23, 43), "Interaction", (7, 13, 23, 43)),
    (4, "Explanation", (4, 49, 23, 43), "Revolution", (4, 49, 8, 14), "Formulization", (4, 49, 8, 14)),
    (29, "Contagion", (29, 30, 8, 14), "Industry", (29, 30, 20, 34), "Commitment", (29, 30, 20, 34)),
    (59, "The Sleeping Phoenix", (59, 55, 20, 34), "Spirit", (59, 55, 16, 9), "Strategy", (59, 55, 16, 9)),
    (40, "Planning", (40, 37, 16, 9), "Migration", (40, 37, 35, 5), "Denial", (40, 37, 35, 5)),
    (64, "Consciousness", (64, 63, 35, 5), "Dominion", (64, 63, 45, 26), "Confusion", (64, 63, 45, 26)),
    (47, "Rulership", (47, 22, 45, 26), "Informing", (47, 22, 12, 11), "Oppression", (47, 22, 12, 11)),
    (6, "Eden", (6, 36, 12, 11), "The Plane", (6, 36, 15, 10), "Conflict", (6, 36, 15, 10)),
    (46, "The Vessel of Love", (46, 25, 15, 10), "Healing", (46, 25, 52, 58), "Serendipity", (46, 25, 52, 58)),
    (18, "Service", (18, 17, 52, 58), "Upheaval", (18, 17, 39, 38), "Correction", (18, 17, 39, 38)),
    (48, "Tension", (48, 21, 39, 38), "Endeavor", (48, 21, 53, 54), "Depth", (48, 21, 53, 54)),
    (57, "Penetration", (57, 51, 53, 54), "The Clarion", (57, 51, 62, 61), "Intuition", (57, 51, 62, 61)),
    (32, "Maya", (32, 42, 62, 61), "Limitation", (32, 42, 56, 60), "Conservation", (32, 42, 56, 60)),
    (50, "Laws", (50, 3, 56, 60), "Wishes", (50, 3, 31, 41), "Values", (50, 3, 31, 41)),
    (28, "The Unexpected", (28, 27, 31, 41), "Alignment", (28, 27, 33, 19), "Risks", (28, 27, 33, 19)),
    (44, "The Four Ways", (44, 24, 33, 19), "Incarnation", (44, 24, 7, 13), "Alertness", (44, 24, 7, 13)),
    # Quarter 4: Mutation
    (1, "The Sphinx", (1, 2, 7, 13), "Defiance", (1, 2, 4, 49), "Self Expression", (1, 2, 4, 49)),
    (43, "Explanation", (43, 23, 4, 49), "Dedication", (43, 23, 29, 30), "Insight", (43, 23, 29, 30)),
    (14, "Contagion", (14, 8, 29, 30), "Uncertainty", (14, 8, 59, 55), "Empowering", (14, 8, 59, 55)),
    (34, "The Sleeping Phoenix", (34, 20, 59, 55), "Duality", (34, 20, 40, 37), "Power", (34, 20, 40, 37)),
    (9, "Planning", (9, 16, 40, 37), "Identification", (9, 16, 64, 63), "Focus", (9, 16, 64, 63)),
    (5, "Consciousness", (5, 35, 64, 63), "Separation", (5, 35, 47, 22), "Habits", (5, 35, 47, 22)),
    (26, "Rulership", (26, 45, 47, 22), "Confrontation", (26, 45, 6, 36), "The Trickster", (26, 45, 6, 36)),
    (11, "Eden", (11, 12, 6, 36), "Education", (11, 12, 46, 25), "Ideas", (11, 12, 46, 25)),
    (10, "The Vessel of Love", (10, 15, 46, 25), "Prevention", (10, 15, 18, 17), "Behavior", (10, 15, 18, 17)),
    (58, "Service", (58, 52, 18, 17), "Demands", (58, 52, 48, 21), "Vitality", (58, 52, 48, 21)),
    (38, "Tension", (38, 39, 48, 21), "Individualism", (38, 39, 57, 51), "Opposition", (38, 39, 57, 51)),
    (54, "Penetration", (54, 53, 57, 51), "Cycles", (54, 53, 32, 42), "Ambition", (54, 53, 32, 42)),
    (61, "Maya", (61, 62, 32, 42), "Obscuration", (61, 62, 50, 3), "Thinking", (61, 62, 50, 3)),
    (60, "Laws", (60, 56, 50, 3), "Distraction", (60, 56, 28, 27), "Limitation", (60, 56, 28, 27)),
    (41, "The Unexpected", (41, 31, 28, 27), "The Alpha", (41, 31, 44, 24), "Fantasy", (41, 31, 44, 24)),
    (19, "The Four Ways", (19, 33, 44, 24), "Refinement", (19, 33, 1, 2), "Need", (19, 33, 1, 2)),
]

# Tên tiếng Việt theo (họ, tên gốc). JX mỗi tên là duy nhất nên không cần họ.
NAME_VI = {
    ("RAX", "The Sphinx"): "Nhân Sư",
    ("RAX", "Explanation"): "Lý Giải",
    ("RAX", "Contagion"): "Lan Tỏa",
    ("RAX", "The Sleeping Phoenix"): "Phượng Hoàng Ngủ",
    ("RAX", "Planning"): "Kế Hoạch",
    ("RAX", "Consciousness"): "Ý Thức",
    ("RAX", "Rulership"): "Cai Trị",
    ("RAX", "Eden"): "Địa Đàng",
    ("RAX", "The Vessel of Love"): "Con Tàu Tình Yêu",
    ("RAX", "Service"): "Phục Vụ",
    ("RAX", "Tension"): "Căng Thẳng",
    ("RAX", "Penetration"): "Xuyên Thấu",
    ("RAX", "Maya"): "Ảo Ảnh",
    ("RAX", "Laws"): "Luật Lệ",
    ("RAX", "The Unexpected"): "Bất Ngờ",
    ("RAX", "The Four Ways"): "Bốn Con Đường",
    ("LAX", "Masks"): "Mặt Nạ",
    ("LAX", "Revolution"): "Cách Mạng",
    ("LAX", "Industry"): "Nghề Nghiệp",
    ("LAX", "Spirit"): "Tinh Thần",
    ("LAX", "Migration"): "Di Cư",
    ("LAX", "Dominion"): "Thống Trị",
    ("LAX", "Informing"): "Thông Tin",
    ("LAX", "The Plane"): "Trần Gian",
    ("LAX", "Healing"): "Chữa Lành",
    ("LAX", "Upheaval"): "Biến Động",
    ("LAX", "Endeavor"): "Nỗ Lực",
    ("LAX", "The Clarion"): "Tiếng Kèn",
    ("LAX", "Limitation"): "Giới Hạn",
    ("LAX", "Wishes"): "Ước Nguyện",
    ("LAX", "Alignment"): "Căn Chỉnh",
    ("LAX", "Incarnation"): "Hóa Thân",
    ("LAX", "Defiance"): "Thách Thức",
    ("LAX", "Dedication"): "Cống Hiến",
    ("LAX", "Uncertainty"): "Bất Định",
    ("LAX", "Duality"): "Đối Ngẫu",
    ("LAX", "Identification"): "Định Danh",
    ("LAX", "Separation"): "Tách Biệt",
    ("LAX", "Confrontation"): "Đối Đầu",
    ("LAX", "Education"): "Giáo Dục",
    ("LAX", "Prevention"): "Ngăn Ngừa",
    ("LAX", "Demands"): "Yêu Sách",
    ("LAX", "Individualism"): "Cá Tính",
    ("LAX", "Cycles"): "Chu Kỳ",
    ("LAX", "Obscuration"): "Màn Mờ",
    ("LAX", "Distraction"): "Xao Nhãng",
    ("LAX", "The Alpha"): "Đầu Đàn",
    ("LAX", "Refinement"): "Tinh Luyện",
    ("JX", "Listening"): "Lắng Nghe",
    ("JX", "Principles"): "Nguyên Tắc",
    ("JX", "Fates"): "Số Phận",
    ("JX", "Moods"): "Tâm Trạng",
    ("JX", "Bargains"): "Thỏa Thuận",
    ("JX", "Doubts"): "Nghi Ngờ",
    ("JX", "Grace"): "Duyên Dáng",
    ("JX", "Crisis"): "Khủng Hoảng",
    ("JX", "Innocence"): "Ngây Thơ",
    ("JX", "Opinions"): "Quan Điểm",
    ("JX", "Control"): "Kiểm Soát",
    ("JX", "Shock"): "Cú Sốc",
    ("JX", "Completion"): "Hoàn Tất",
    ("JX", "Mutation"): "Đột Biến",
    ("JX", "Caring"): "Chăm Sóc",
    ("JX", "Rationalization"): "Hợp Lý Hóa",
    ("JX", "The Driver"): "Người Cầm Lái",
    ("JX", "Assimilation"): "Đồng Hóa",
    ("JX", "Contribution"): "Đóng Góp",
    ("JX", "The Now"): "Hiện Tại",
    ("JX", "Experimentation"): "Thực Nghiệm",
    ("JX", "Experience"): "Trải Nghiệm",
    ("JX", "Possession"): "Sở Hữu",
    ("JX", "Articulation"): "Diễn Đạt",
    ("JX", "Extremes"): "Cực Đoan",
    ("JX", "Stillness"): "Tĩnh Lặng",
    ("JX", "Provocation"): "Khiêu Khích",
    ("JX", "Beginnings"): "Khởi Đầu",
    ("JX", "Detail"): "Chi Tiết",
    ("JX", "Stimulation"): "Kích Thích",
    ("JX", "Influence"): "Ảnh Hưởng",
    ("JX", "Retreat"): "Thoái Lui",
    ("JX", "Interaction"): "Tương Tác",
    ("JX", "Formulization"): "Công Thức Hóa",
    ("JX", "Commitment"): "Cam Kết",
    ("JX", "Strategy"): "Chiến Lược",
    ("JX", "Denial"): "Từ Chối",
    ("JX", "Confusion"): "Rối Rắm",
    ("JX", "Oppression"): "Áp Bức",
    ("JX", "Conflict"): "Xung Đột",
    ("JX", "Serendipity"): "Cơ Duyên",
    ("JX", "Correction"): "Chỉnh Sửa",
    ("JX", "Depth"): "Chiều Sâu",
    ("JX", "Intuition"): "Trực Giác",
    ("JX", "Conservation"): "Bảo Tồn",
    ("JX", "Values"): "Giá Trị",
    ("JX", "Risks"): "Rủi Ro",
    ("JX", "Alertness"): "Cảnh Giác",
    ("JX", "Self Expression"): "Tự Thể Hiện",
    ("JX", "Insight"): "Sáng Kiến",
    ("JX", "Empowering"): "Trao Quyền",
    ("JX", "Power"): "Sức Mạnh",
    ("JX", "Focus"): "Tập Trung",
    ("JX", "Habits"): "Thói Quen",
    ("JX", "The Trickster"): "Kẻ Đánh Lừa",
    ("JX", "Ideas"): "Ý Tưởng",
    ("JX", "Behavior"): "Hành Vi",
    ("JX", "Vitality"): "Sức Sống",
    ("JX", "Opposition"): "Chống Đối",
    ("JX", "Ambition"): "Tham Vọng",
    ("JX", "Thinking"): "Suy Ngẫm",
    ("JX", "Limitation"): "Giới Hạn",
    ("JX", "Fantasy"): "Mộng Tưởng",
    ("JX", "Need"): "Nhu Cầu",
}

# Nghĩa một dòng (tự viết từ cơ học cổng). RAX/LAX dùng chung theo tên.
MEANING_VI = {
    ("RAX", "The Sphinx"): "Hiện thân để định hướng: sống đúng thiết kế của mình là tự nhiên dẫn người khác tìm phương hướng.",
    ("RAX", "Explanation"): "Mang lý thuyết và lời giải thích khác biệt giúp cộng đồng thay niềm tin sai lầm.",
    ("RAX", "Contagion"): "Truyền cảm hứng qua đam mê cá nhân; khai phá nền tảng mới tạo trào lưu.",
    ("RAX", "The Sleeping Phoenix"): "Biến đổi qua hiện diện: giữ nhịp sống đúng để sức mạnh và độc lập cảm xúc tự nở.",
    ("RAX", "Planning"): "Lập kế hoạch chi tiết cho cộng đồng dựa trên ưu tiên chung; tập trung vào mục tiêu cuối.",
    ("RAX", "Consciousness"): "Hòa vào dòng chảy nhịp điệu tự nhiên của cuộc sống và chia sẻ giác ngộ đó.",
    ("RAX", "Rulership"): "Cai trị thế giới của mình một cách duyên dáng qua lắng nghe và giáo dục.",
    ("RAX", "Eden"): "Khám phá thế giới vật chất để tìm một phần địa đàng trên trần gian và chia sẻ.",
    ("RAX", "The Vessel of Love"): "Hiện thân tình yêu: tìm thấy tình yêu bản thân để thành tấm gương yêu thương.",
    ("RAX", "Service"): "Hướng dẫn và tổ chức để giúp mọi người đạt cuộc sống khỏe mạnh, vui vẻ hơn.",
    ("RAX", "Tension"): "Dùng căng thẳng và khiêu khích đúng lúc để duy trì trật tự và liên kết cộng đồng.",
    ("RAX", "Penetration"): "Đi thẳng vào trọng tâm vấn đề để dọn đường cho kết quả.",
    ("RAX", "Maya"): "Đưa cái chưa biết vào cái biết; khiến thế giới đánh giá lại vị trí trước ý tưởng mới.",
    ("RAX", "Laws"): "Thiết lập và giữ quy định để giảm lo âu; thay đổi luật dần dần, tránh hỗn loạn.",
    ("RAX", "The Unexpected"): "Chăm sóc cộng đồng và đón điều bất ngờ nảy sinh như một phần của sống.",
    ("RAX", "The Four Ways"): "Tìm hiểu sâu cách vạn vật vận hành qua lặp lại trải nghiệm trên bốn đường sinh tồn-tâm linh.",
    ("LAX", "Masks"): "Được kỳ vọng dẫn đầu khi cấp bách; chuẩn bị kỹ thì đeo mặt nạ nào cũng thành công.",
    ("LAX", "Revolution"): "Thực hiện thay đổi thiết thực khi mô hình cách mạng khớp với sự thật.",
    ("LAX", "Industry"): "Hoạt động hiệu quả và cần cù nhất khi tìm thấy đam mê cốt lõi của tâm hồn.",
    ("LAX", "Spirit"): "Dẫn dắt bằng tinh thần qua gắn kết thân mật: biến cảm hứng thành kỹ năng nuôi cộng đồng.",
    ("LAX", "Migration"): "Dẫn cộng đồng di chuyển theo nhịp mới: rời cái cũ đúng lúc để đến nơi nuôi sống tốt hơn.",
    ("LAX", "Dominion"): "Nắm quyền hành dựa trên thông tin lịch sử; cân nhắc hậu quả nghiệp báo khi quyết định.",
    ("LAX", "Informing"): "Thu thập và phân phối thông tin hùng hồn cho cộng đồng và xã hội.",
    ("LAX", "The Plane"): "Hướng dẫn thành công trong thế giới vật chất bằng cách sống phù hợp thiết kế linh hồn.",
    ("LAX", "Healing"): "Truyền đạt giá trị sức khỏe và hàn gắn qua trải nghiệm cá nhân.",
    ("LAX", "Upheaval"): "Khuấy động vấn đề trì trệ để truyền cảm hứng sàng lọc và sửa chữa.",
    ("LAX", "Endeavor"): "Tập hợp nguồn lực nhỏ để thực hiện nỗ lực lớn qua kiểm soát chặt chẽ.",
    ("LAX", "The Clarion"): "Tiếng kèn thức tỉnh: cú sốc trực giác đúng lúc đánh thức cộng đồng khỏi u mê.",
    ("LAX", "Limitation"): "Xác định và truyền đạt về hạn chế cần thiết để thành công và tồn tại.",
    ("LAX", "Wishes"): "Lãnh đạo thay đổi luật pháp dựa trên ước muốn về tương lai tốt đẹp hơn.",
    ("LAX", "Alignment"): "Căn chỉnh cộng đồng qua biến cố: chăm sóc đúng nhu cầu để mọi người về đúng hàng.",
    ("LAX", "Incarnation"): "Định hướng cho chu kỳ sống dựa trên hiểu biết về quá trình đến và đi.",
    ("LAX", "Defiance"): "Thách thức quy tắc áp đặt giới hạn lên thể hiện bản thân; đại diện cách làm khác biệt.",
    ("LAX", "Dedication"): "Cống hiến cho việc giảng dạy và làm sáng tỏ thông điệp qua kể lại.",
    ("LAX", "Uncertainty"): "Đối mặt thăng trầm cảm xúc để tìm niềm vui trong mong muốn vật chất và an toàn.",
    ("LAX", "Duality"): "Cầu nối hai thế giới cá nhân-cộng đồng: hiện diện trong hiện tại để thử lửa sự gắn kết.",
    ("LAX", "Identification"): "Đóng góp dựa trên ổn định và an toàn; tập trung mạnh mẽ mang lại thành quả cụ thể.",
    ("LAX", "Separation"): "Tìm kiếm và sống theo nhịp điệu riêng biệt, cung cấp hình mẫu độc lập.",
    ("LAX", "Confrontation"): "Đối mặt quyền cai trị cũ để đưa ra thông tin và hiểu biết sâu sắc hơn.",
    ("LAX", "Education"): "Đề xướng giáo dục như phương tiện để con người hiểu mình và phát triển.",
    ("LAX", "Prevention"): "Phân tích và sửa chữa hành vi để ngăn thảm họa tiềm tàng; bảo vệ người khác khỏi rủi ro.",
    ("LAX", "Demands"): "Yêu cầu hành động để khắc phục vấn đề không hiệu quả trong xã hội tập thể.",
    ("LAX", "Individualism"): "Bảo vệ tính cá nhân qua khiêu khích: cú hích trực giác giúp cộng đồng tôn trọng khác biệt.",
    ("LAX", "Cycles"): "Xử lý chu kỳ tiến hóa lặp đi lặp lại để thúc đẩy trưởng thành vạn vật.",
    ("LAX", "Obscuration"): "Đặt câu hỏi và xem xét hình mẫu để tìm viễn cảnh hợp lý cho thực tại.",
    ("LAX", "Distraction"): "Biến xao nhãng thành tỉnh thức: giữa ồn ào vẫn giữ chăm sóc và giới hạn đúng.",
    ("LAX", "The Alpha"): "Lãnh đạo nhóm và đảm bảo nhu cầu sinh tồn, giảm bớt nỗi sợ hãi cho tập thể.",
    ("LAX", "Refinement"): "Đưa ra định hướng lâu dài về tồn tại bền vững và nguồn lực cho xã hội.",
    ("JX", "Listening"): "Thu thập bí mật và lịch sử; hợp vai trò đòi hỏi lắng nghe và giữ bí mật cao.",
    ("JX", "Principles"): "Sống chết với nguyên tắc: biến giá trị thành của cải và đóng góp cụ thể.",
    ("JX", "Fates"): "Tiến lên bằng ám ảnh và đam mê; đốt cháy năng lượng để đạt khám phá mới.",
    ("JX", "Moods"): "Làm chủ tâm trạng: biến sóng cảm xúc thành kỹ năng tập trung nuôi gắn kết.",
    ("JX", "Bargains"): "Nghệ thuật thỏa thuận: mặc cả nhịp nhàng để cộng đồng đổi thay mà vẫn gắn bó.",
    ("JX", "Doubts"): "Kỹ sư an toàn của xã hội; dùng nghi ngờ để đảm bảo quy trình chạy không rủi ro.",
    ("JX", "Grace"): "Người biết lắng nghe duyên dáng, tạo tin cậy bản năng với người lạ.",
    ("JX", "Crisis"): "Đi xuyên khủng hoảng cảm xúc để chạm cực đoan của yêu thương và trưởng thành.",
    ("JX", "Innocence"): "Ảnh hưởng thế giới bằng tình yêu sống và niềm vui tràn đầy sức sống con người.",
    ("JX", "Opinions"): "Đưa ra quan điểm quan trọng để điều chỉnh hành vi xã hội.",
    ("JX", "Control"): "Nắm quyền kiểm soát để tái tạo và mang lại đổi mới thực sự.",
    ("JX", "Shock"): "Cú sốc thức tỉnh đúng chỗ: trực giác biết chạm đâu để sự thật lộ ra.",
    ("JX", "Completion"): "Đi trọn chu kỳ: kết thúc trong giới hạn để mở đầu mới đầy cảm hứng.",
    ("JX", "Mutation"): "Lực lượng đột biến thay đổi quy tắc cộng đồng; thường bị coi là bất đồng chính kiến.",
    ("JX", "Caring"): "Mang lại chăm sóc cho vạn vật để tìm ra mục đích sống.",
    ("JX", "Rationalization"): "Nắm bắt khái niệm sáng giá và hợp lý hóa chúng trong dòng chảy lịch sử.",
    ("JX", "The Driver"): "Tự định hướng và khám phá sự thật bản thân cùng người xung quanh, kéo mọi người về phía hiểu biết.",
    ("JX", "Assimilation"): "Đưa ra ý tưởng mới để tạo thay đổi mà không gây sợ hãi qua đồng hóa dần dần.",
    ("JX", "Contribution"): "Đóng góp xã hội bằng cách điều chỉnh, sửa chữa và làm dự án tốt đẹp hơn.",
    ("JX", "The Now"): "Hình mẫu cho hiện diện trong giây phút hiện tại kết nối với cộng đồng.",
    ("JX", "Experimentation"): "Quyết tâm biến điều hứng thú thành hiện thực dù khó giải thích.",
    ("JX", "Experience"): "Sống để trải nghiệm: gom nhặt đổi thay thành nhận thức chín cho cộng đồng.",
    ("JX", "Possession"): "Giữ của chung: gom nguồn lực và vượt ma sát cảm xúc để phân phối công bằng.",
    ("JX", "Articulation"): "Thốt đúng lời đúng lúc: diễn đạt ý tưởng bằng cả tinh thần hiện diện.",
    ("JX", "Extremes"): "Tìm kiếm nhịp điệu bên trong những thái cực hành vi và cuộc sống.",
    ("JX", "Stillness"): "Đưa ra lời khuyên hiền triết từ điểm tĩnh lặng bẩm sinh; quan sát rõ mọi giải pháp.",
    ("JX", "Provocation"): "Khiêu khích chữa lành: chạm đúng chỗ đau bằng trực giác để giải phóng tắc nghẽn.",
    ("JX", "Beginnings"): "Bậc thầy khởi đầu: gieo tham vọng đúng lúc để chu kỳ mới bền lâu.",
    ("JX", "Detail"): "Thượng tôn chi tiết: sắp xếp điều nhỏ theo giá trị để bức tranh lớn hiện ra.",
    ("JX", "Stimulation"): "Kích thích đúng liều: kể chuyện truyền cảm hứng trong giới hạn của chăm sóc.",
    ("JX", "Influence"): "Ảnh hưởng bằng định hướng: gom kỳ vọng thành lời dẫn có cơ sở.",
    ("JX", "Retreat"): "Mang lại ảnh hưởng về quyền có nơi ẩn náu và không gian riêng cho mỗi người.",
    ("JX", "Interaction"): "Đóng góp vào tổ chức qua mối quan hệ tương tác.",
    ("JX", "Formulization"): "Diễn đạt lý thuyết về mẫu và công thức để giải thích mọi thứ cho thế giới.",
    ("JX", "Commitment"): "Tận tâm với điều đã thỏa thuận và truyền cảm hứng trách nhiệm cho người khác.",
    ("JX", "Strategy"): "Chiến lược gắn kết: dùng kỹ năng và tập trung để thân mật đơm hoa đúng mùa.",
    ("JX", "Denial"): "Biết nói không: từ chối để bảo vệ nhịp cộng đồng khỏi đổi thay sai lúc.",
    ("JX", "Confusion"): "Đi xuyên rối rắm: gom mảnh vụn nghi ngờ thành nguồn lực rõ ràng.",
    ("JX", "Oppression"): "Biến áp bức thành thấu hiểu: nén đủ lâu để lời bật ra đúng và thấm.",
    ("JX", "Conflict"): "Tìm kiếm cân bằng giữa nỗi đau mất mát và niềm vui sống qua mối quan hệ.",
    ("JX", "Serendipity"): "Ngẫu nhiên may mắn: hiện diện đúng nơi, tình cờ hóa thành định mệnh đẹp.",
    ("JX", "Correction"): "Sửa mẫu để khám phá cuộc sống vui tươi; cần tế nhị trong giao tiếp.",
    ("JX", "Depth"): "Chiều sâu tạo quyền: đủ sâu mới dám cầm lái khởi đầu lớn.",
    ("JX", "Intuition"): "Trực giác sắc bén: nghe rung cảm hiện tại để xuyên qua bí ẩn.",
    ("JX", "Conservation"): "Bảo vệ sự sống và môi trường; chuẩn bị cho biến cố để duy trì tồn tại.",
    ("JX", "Values"): "Giữ giá trị cốt lõi: sắp xếp trật tự để ước mơ chung có chỗ bám.",
    ("JX", "Risks"): "Sẵn sàng chấp nhận rủi ro để tìm kiếm mục đích và ý nghĩa sâu sắc.",
    ("JX", "Alertness"): "Cảnh giác lịch sử: đánh hơi từ quá khứ để dẫn dắt đúng lúc.",
    ("JX", "Self Expression"): "Sinh ra để khác biệt và làm điều riêng biệt; thể hiện cá nhân giúp xã hội ủng hộ ý tưởng mới.",
    ("JX", "Insight"): "Insight đột phá: nói ra điều mới đúng lúc cam kết chín muồi.",
    ("JX", "Empowering"): "Đạt hạnh phúc qua an toàn tài chính và tình cảm để trao quyền cá nhân.",
    ("JX", "Power"): "Chia sẻ sức mạnh và trao đổi năng lượng để đạt ý nguyện sâu thẳm tâm hồn.",
    ("JX", "Focus"): "Tìm kiếm tập trung qua thư giãn thay vì gượng ép logic.",
    ("JX", "Habits"): "Ảnh hưởng mạnh đến khuôn mẫu xã hội bằng cách chứng minh sức mạnh nhịp điệu qua thói quen cá nhân.",
    ("JX", "The Trickster"): "Tiếp thị và lôi kéo mọi người tin vào ý tưởng mới chưa có bằng chứng.",
    ("JX", "Ideas"): "Hệ thống hóa tư duy về trải nghiệm thể chất và gửi thông điệp triết học đến thế giới.",
    ("JX", "Behavior"): "Hướng dẫn và điều chỉnh hành vi người khác để đạt niềm vui sống lớn hơn.",
    ("JX", "Vitality"): "Sức sống lan tỏa: tĩnh đủ sâu để niềm vui thành quyền năng chữa lành.",
    ("JX", "Opposition"): "Chống đối chính nghĩa: đứng về phía trực giác dù phải gây sốc.",
    ("JX", "Ambition"): "Tham vọng có rễ: khởi đầu khiêm tốn, bền bỉ đến ngày nở hoa.",
    ("JX", "Thinking"): "Tư duy truy nguyên: hỏi đến cùng để sắp xếp lại giá trị từ gốc.",
    ("JX", "Limitation"): "Chấp nhận giới hạn: trong khuôn khổ vẫn dám liều vì điều đáng chăm sóc.",
    ("JX", "Fantasy"): "Mơ để dẫn: biến kỳ vọng thành tầm nhìn có cơ sở thực tế.",
    ("JX", "Need"): "Nhu cầu biểu đạt sáng tạo trong không gian cá nhân riêng biệt.",
}


def _build():
    crosses = {}
    for row in _RAW:
        p_gate, rax_name, rax_gates, lax_name, lax_gates, jx_name, jx_gates = row
        crosses[(p_gate, "RAX")] = {"name_en": rax_name, "gates": rax_gates}
        crosses[(p_gate, "LAX")] = {"name_en": lax_name, "gates": lax_gates}
        crosses[(p_gate, "JX")] = {"name_en": jx_name, "gates": jx_gates}
    return crosses


CROSSES = _build()


def get_cross(p_sun_gate: int, geom: str) -> dict:
    """Tra một Cross theo cổng Sun ý thức + họ (RAX/LAX/JX)."""
    entry = CROSSES[(int(p_sun_gate), geom)]
    return {
        "name_en": entry["name_en"],
        "name_vi": NAME_VI[(geom, entry["name_en"])],
        "gates": entry["gates"],
        "geom_vi": GEOM_VI[geom],
        "profiles": PROFILES[geom],
        "meaning_vi": MEANING_VI[(geom, entry["name_en"])],
    }


def quarter_of(p_sun_gate: int) -> int:
    for q, info in QUARTERS.items():
        if int(p_sun_gate) in info["gates"]:
            return q
    raise KeyError(p_sun_gate)


def verify() -> list[str]:
    """Kiểm tra cơ học toàn bảng 192. Trả về danh sách lỗi (rỗng = đạt)."""
    from hd_calculator import (GATE_ORDER, START_LONGITUDE, DEG_PER_GATE,
                               longitude_to_gate_line)
    errors = []
    if len(CROSSES) != 192:
        errors.append(f"count={len(CROSSES)}")
    for (p_gate, geom), entry in sorted(CROSSES.items()):
        g1, g2, g3, g4 = entry["gates"]
        if g1 != p_gate:
            errors.append(f"{p_gate}/{geom}: P-Sun {g1} != key")
        want_earth = GATE_ORDER[(GATE_ORDER.index(g1) + 32) % 64]
        if g2 != want_earth:
            errors.append(f"{p_gate}/{geom}: P-Earth {g2} != đối diện {want_earth}")
        i = GATE_ORDER.index(g1)
        p_start = (START_LONGITUDE + i * DEG_PER_GATE) % 360
        # RAX = D-sớm (đầu cổng), JX/LAX = D-muộn (cuối cổng); biên nằm giữa Dòng 4.
        probe = 1.0 if geom == "RAX" else 5.0
        want_d = longitude_to_gate_line((p_start + probe - 88) % 360)["gate"]
        if g3 != want_d:
            errors.append(f"{p_gate}/{geom}: D-Sun {g3} != suy từ 88° ({want_d})")
        want_de = GATE_ORDER[(GATE_ORDER.index(g3) + 32) % 64]
        if g4 != want_de:
            errors.append(f"{p_gate}/{geom}: D-Earth {g4} != đối diện {want_de}")
        key = (geom, entry["name_en"])
        if key not in NAME_VI:
            errors.append(f"{p_gate}/{geom}: thiếu tên VI cho {entry['name_en']}")
        if key not in MEANING_VI:
            errors.append(f"{p_gate}/{geom}: thiếu nghĩa VI cho {entry['name_en']}")
    seen_quarters = {quarter_of(g) for g in range(1, 65)}
    if seen_quarters != {1, 2, 3, 4}:
        errors.append(f"quarter coverage: {seen_quarters}")
    return errors


def render_markdown() -> str:
    """Sinh nội dung danh mục 192 cho knowledge/08 (giữ đồng bộ với bảng)."""
    out = []
    for q in (1, 2, 3, 4):
        info = QUARTERS[q]
        out.append(f"### Quarter {q}: {info['en']} — {info['vi']} ({info['theme']})")
        out.append("")
        for g in info["gates"]:
            names = []
            for geom in ("RAX", "LAX", "JX"):
                c = get_cross(g, geom)
                a, b, c3, d = c["gates"]
                profs = ", ".join(c["profiles"])
                plabel = "Profile" if geom == "JX" else "Profiles"
                names.append(
                    f"- **{geom} {c['name_en']} · {c['name_vi']}** "
                    f"[{a}/{b} | {c3}/{d}] — {plabel} {profs}: {c['meaning_vi']}"
                )
            out.append(f"#### Sun {g}")
            out.append("")
            out.extend(names)
            out.append("")
    return "\n".join(out).rstrip() + "\n"

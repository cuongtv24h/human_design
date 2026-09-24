"""
Human Design General Consultation Tool - Áp dụng cho TẤT CẢ Types/Profiles
Tích hợp từ Wiki Phân mục 6 - Quy trình tham vấn 4 bước chuyên nghiệp + Deep dive cho từng Type

- 5 Types: Manifestor (9%), Generator (36%), MG (32%), Projector (22%), Reflector (1%)
- 12 Profiles: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3
- Tổng: 60 biến thể

Tác giả: Build theo yêu cầu - 2026-09-23
"""

from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER, CHANNEL_TO_CENTERS
from hd_advanced_tools import analyze_fear_gates, analyze_love_gates
import datetime as dt_module
from datetime import datetime
import json

# ==================== DEEP DIVE CHO TỪNG TYPE ====================

TYPE_DEEP_DIVE = {
    "Manifestor": {
        "aura": "Aura đóng và mang tính đẩy lùi, bộc phát đột ngột khiến người xung quanh e dè hoặc sợ hãi. Cảm giác khác biệt ngay từ nhỏ.",
        "psychology": [
            "Hăng hái, mạnh mẽ và bốc đồng",
            "Năng lượng không bền vững - thiết kế để BẮT ĐẦU mọi thứ nhưng không có năng lượng bền bỉ để thực hiện tất cả như Generator",
            "Độc lập cao, không thích bị kiểm soát hoặc bị bảo phải làm gì",
            "Nếu cố làm tất cả, dễ đối mặt vấn đề nghiêm trọng về sức khỏe (tim mạch, gan, hệ thần kinh)"
        ],
        "strategy": {
            "name": "Informing - Thông báo",
            "description": "Chìa khóa để Manifestor vận hành êm thấm. Cần thông báo cho những người bị ảnh hưởng trước khi hành động. Không phải xin phép mà là cách loại bỏ phản kháng bên ngoài và giúp người khác an tâm.",
            "practice": "Trước khi hành động, nói: 'Tôi sẽ làm...' cho những người bị ảnh hưởng. Ví dụ: 'Tôi sẽ đi ra ngoài 1 tiếng' thay vì đứng dậy đi luôn."
        },
        "signature": {"name": "Peace - Bình yên", "description": "Khi thực hiện đúng Strategy Informing, đạt trạng thái bình yên, thuận lợi trong hành động và thỏa mãn tâm hồn"},
        "not_self": {"name": "Anger - Giận dữ", "description": "Nguồn gốc từ việc bị hạn chế quyền tự do. Cảm giác bị trừng phạt khi bị kiểm soát bởi quy tắc nghiêm khắc tích tụ thành tâm lý tức giận, bạo lực và xa cách xã hội. Đặc biệt nghiêm trọng ở nam giới bị kìm kẹp từ nhỏ.", "healing": "Học cách Inform để giảm phản kháng, từ đó tìm thấy bình an nội tại"},
        "work": {"suitable": ["Khởi nghiệp", "Lãnh đạo", "Vai trò khởi xướng", "Tiên phong", "Tạo tác động"], "needs": ["Tự chủ", "Không bị quản lý chặt", "Làm việc theo đợt bộc phát, không đều đặn 8h/ngày"], "team": "Cần Generator/MG để thực thi sau khi khởi xướng, cần Projector để hướng dẫn quản lý năng lượng"},
        "relationship": {"aura_impact": "Aura đóng, đẩy -> người khác e dè, cảm thấy bị đẩy ra", "needs": ["Tự do", "Không thích bị kiểm soát", "Học cách thông báo cho đối phương"], "seeking": "Bình yên, không phải ai cũng hiểu"},
        "child": {
            "description": "Trẻ em Manifestor bẩm sinh đã biết mình muốn làm gì và khi nào cần làm",
            "wound": "Khi cha mẹ/giáo viên áp đặt rào cản do lo ngại sự tự ý của trẻ, vô tình tạo ra hình phạt tâm lý. Trẻ bị kìm kẹp lớn lên với xu hướng phản ứng mạnh mẽ hoặc bạo lực",
            "advice": ["Đừng kiểm soát, hãy cho tự chủ trong khuôn khổ an toàn", "Dạy trẻ cách thông báo: 'Con sẽ làm...' thay vì xin phép", "Tôn trọng sự độc lập", "Cho không gian riêng", "Hiểu trẻ không có năng lượng bền bỉ như Generator, cần nghỉ ngơi", "Đừng trừng phạt khi trẻ tự ý - hỏi 'Con đã thông báo chưa?'", "Khen ngợi khi trẻ thông báo"]
        }
    },
    "Generator": {
        "aura": "Aura mở, bao bọc, hút. Là thỏi nam châm thu hút cơ hội. Nguồn năng lượng bền bỉ của hành tinh.",
        "psychology": [
            "Có năng lượng bền bỉ để làm việc, xây dựng, sáng tạo - NẾU làm việc mình yêu",
            "Sacral là la bàn: uh-huh (âm thanh mở, cao, ngực nở) = CÓ, uh-uh (đóng, thấp, co lại) = KHÔNG",
            "Không được thiết kế để khởi xướng, mà để ĐÁP ỨNG",
            "Kiệt sức Sacral: Không đơn thuần mệt mỏi mà là cạn kiệt nguồn sinh lực do sử dụng năng lượng vào việc không có phản hồi tự thân"
        ],
        "strategy": {
            "name": "Wait to Respond - Chờ để Đáp Ứng",
            "description": "Đừng khởi xướng. Chờ cuộc sống mang đến tín hiệu (câu hỏi, cơ hội, người), rồi để Sacral phản ứng. Đừng quyết định bằng đầu óc.",
            "practice": "Hỏi câu hỏi có/không thay vì mở. Ví dụ: Thay vì 'Bạn muốn làm gì?', hỏi 'Bạn có muốn làm X không?' và lắng nghe tiếng bụng."
        },
        "signature": {"name": "Satisfaction - Hài lòng", "description": "Khi làm công việc yêu thích, sử dụng năng lượng đúng cách, cảm thấy thỏa mãn sâu sắc"},
        "not_self": {"name": "Frustration - Thất vọng", "description": "Khi làm việc không yêu thích, ép bản thân khởi xướng, không lắng nghe Sacral. Dấu hiệu sống sai thiết kế. Frustration là tín hiệu để dừng và hỏi lại Sacral.", "healing": "Quay về lắng nghe Sacral, chỉ làm việc mang lại Satisfaction"},
        "work": {"suitable": ["Công việc cần bền bỉ, xây dựng, làm việc lâu dài", "Nghề thủ công, xây dựng, chăm sóc, sáng tạo", "Bất kỳ việc gì BẠN YÊU - Sacral sẽ cho năng lượng vô tận"], "needs": ["Làm việc mình yêu", "Được hỏi câu hỏi có/không", "Không bị ép khởi xướng"], "team": "Là nguồn năng lượng cho team, cần Projector hướng dẫn và Manifestor khởi xướng"},
        "relationship": {"aura_impact": "Aura mở, hút - thu hút mọi người, cơ hội", "needs": ["Được hỏi, không bị ép", "Tôn trọng tiếng Sacral", "Cần thời gian đáp ứng"], "seeking": "Hài lòng trong công việc và mối quan hệ"},
        "child": {
            "description": "Trẻ Generator có năng lượng dồi dào nếu được làm điều mình thích",
            "wound": "Bị ép học/làm việc không yêu thích -> Frustration sớm, kiệt sức Sacral",
            "advice": ["Hỏi con câu hỏi có/không: 'Con có muốn... không?'", "Đừng ép con khởi xướng", "Cho con thử nhiều việc để tìm ra điều con yêu (Sacral uh-huh)", "Tôn trọng khi con nói uh-uh (không)", "Dạy con lắng nghe bụng, không phải đầu óc"]
        }
    },
    "Manifesting Generator": {
        "aura": "Aura mở như Generator nhưng nhanh hơn, đa nhiệm, có khả năng bỏ qua bước. Kết hợp sức mạnh khởi tạo và vận hành bền bỉ.",
        "psychology": [
            "Nhanh, có thể làm tắt, bỏ qua bước - được thiết kế để tìm con đường hiệu quả nhất",
            "Đa đam mê, được phép thay đổi hướng, không cần làm 1 việc cả đời",
            "Vừa có Sacral bền bỉ vừa có Motor nối Throat -> vừa đáp ứng vừa biểu hiện nhanh",
            "Thích đa nhiệm, dễ bỏ qua bước quan trọng cần chú ý"
        ],
        "strategy": {
            "name": "Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo",
            "description": "Giống Generator: Chờ để Đáp Ứng từ Sacral. Sau khi đáp ứng, cần Thông Báo cho những người bị ảnh hưởng trước khi hành động để giảm kháng cự (kế thừa từ Manifestor).",
            "practice": "Bước 1: Chờ tín hiệu, lắng nghe Sacral uh-huh/uh-uh. Bước 2: Nếu uh-huh, thông báo: 'Tôi sẽ làm X' rồi hành động. Cho phép bản thân thay đổi hướng, làm tắt."
        },
        "signature": {"name": "Satisfaction + Peace - Hài lòng + Bình yên", "description": "Khi làm việc yêu thích và thông báo, cảm thấy vừa hài lòng vừa bình yên"},
        "not_self": {"name": "Frustration + Anger - Thất vọng + Giận dữ", "description": "Frustration khi làm việc không yêu thích + Anger khi gặp kháng cự vì không thông báo. MG dễ bị cả 2.", "healing": "Lắng nghe Sacral + Thông báo trước khi hành động + Cho phép thay đổi hướng"},
        "work": {"suitable": ["Công việc đa nhiệm, nhanh, cần hiệu quả", "Khởi nghiệp, dự án đa dạng", "Công việc cho phép thay đổi, thử nghiệm"], "needs": ["Đa dạng, không gò bó 1 việc", "Được làm tắt, tìm đường nhanh", "Thông báo khi đổi hướng"], "team": "Là Generator nhanh, cần thông báo cho team khi đổi hướng đột ngột"},
        "relationship": {"aura_impact": "Aura mở, nhanh - thu hút nhưng cũng khiến người khác không theo kịp", "needs": ["Được phép thay đổi", "Thông báo khi đổi ý", "Tôn trọng tốc độ nhanh"], "seeking": "Hài lòng + Bình yên, được phép đa đam mê"},
        "child": {
            "description": "Trẻ MG nhanh, đa nhiệm, thích thử nhiều thứ cùng lúc",
            "wound": "Bị ép làm 1 việc, làm chậm lại, làm theo từng bước -> Frustration + Anger",
            "advice": ["Cho con thử nhiều việc cùng lúc", "Cho phép con bỏ qua bước nếu con thấy hiệu quả hơn", "Dạy con thông báo khi đổi ý", "Đừng ép con làm 1 việc cả đời", "Hỏi có/không và tôn trọng tốc độ nhanh của con"]
        }
    },
    "Projector": {
        "aura": "Aura tập trung, xuyên thấu, hút vào người khác. Không có năng lượng bền bỉ. Là Non-Energy Being - ở đây để quản lý, hướng dẫn năng lượng người khác, không phải để làm việc như Generator.",
        "psychology": [
            "Bậc thầy đọc năng lượng và quản lý - nhìn thấy người khác, hệ thống",
            "Không có Sacral bền bỉ -> không nên làm việc 8 tiếng như Generator, dễ kiệt sức",
            "Cần được công nhận (recognition) trước khi được mời (invitation)",
            "Thành công đến khi được mời đúng vào việc lớn: tình yêu, công việc, nơi ở, mối quan hệ quan trọng"
        ],
        "strategy": {
            "name": "Wait for the Invitation - Chờ Lời Mời",
            "description": "Chờ đợi sự công nhận và lời mời chính thức, đặc biệt cho 4 việc lớn: Tình yêu, Công việc, Nơi ở, Mối quan hệ quan trọng. Với việc nhỏ hàng ngày có thể tương tác, nhưng để thành công và không cay đắng, cần được công nhận và mời.",
            "practice": "Tập trung vào học hệ thống, hiểu người khác. Đừng cố gắng ép buộc, chứng minh. Chờ lời mời đúng - nó sẽ thay đổi cuộc đời bạn. Khi được mời, bạn sẽ thành công."
        },
        "signature": {"name": "Success - Thành công", "description": "Khi được công nhận đúng và được mời vào việc phù hợp, cảm thấy thành công sâu sắc, được nhìn thấy"},
        "not_self": {"name": "Bitterness - Cay đắng", "description": "Khi không được công nhận, cố gắng như Generator, cố gắng hướng dẫn khi chưa được mời, làm việc quá sức. Cay đắng là tín hiệu sống sai.", "healing": "Ngừng cố gắng như Generator, nghỉ ngơi nhiều, chờ lời mời đúng, tập trung vào hệ thống"},
        "work": {"suitable": ["Quản lý, hướng dẫn, cố vấn, coach, chuyên gia hệ thống", "Quản lý năng lượng, nhân sự, dự án", "Công việc cần nhìn thấy người khác, không cần làm việc bền bỉ"], "needs": ["Được công nhận trước khi được mời", "Không làm việc 8 tiếng", "Nghỉ ngơi nhiều, ngủ một mình để giải phóng năng lượng người khác", "Lương cao cho ít giờ, không phải lương thấp cho nhiều giờ"], "team": "Là người quản lý năng lượng, cần Generator/MG cung cấp năng lượng, cần Manifestor khởi xướng"},
        "relationship": {"aura_impact": "Aura tập trung, xuyên thấu - nhìn thấy sâu vào người khác, người khác cảm thấy được nhìn thấy", "needs": ["Cần được công nhận", "Cần được mời vào mối quan hệ", "Không thích bị ép buộc"], "seeking": "Thành công, được công nhận, được mời đúng"},
        "child": {
            "description": "Trẻ Projector nhạy cảm, nhìn thấy người khác, cần được công nhận",
            "wound": "Bị ép làm việc nhiều như Generator, không được công nhận, bị bỏ qua -> Cay đắng sớm, kiệt sức, cảm thấy vô hình",
            "advice": ["Công nhận con: 'Mẹ thấy con giỏi X'", "Mời con: 'Con có muốn tham gia... không?'", "Đừng ép con làm việc 8 tiếng như Generator", "Cho con nghỉ ngơi nhiều, ngủ một mình", "Dạy con chờ lời mời, không ép buộc", "Hỏi ý kiến con về hệ thống, con nhìn thấy điều người khác không thấy"]
        }
    },
    "Reflector": {
        "aura": "Aura lấy mẫu, phản chiếu, như tắc kè hoa. Thay đổi theo môi trường, theo chu kỳ Mặt Trăng 28-29 ngày. Không có trung tâm nào định nghĩa - cởi mở hoàn toàn.",
        "psychology": [
            "Trung tâm cộng đồng, đánh giá sức khỏe và trạng thái cộng đồng xung quanh",
            "Phản chiếu môi trường - bạn là ai phụ thuộc vào bạn ở đâu và với ai",
            "Cực kỳ nhạy cảm, thấu cảm, nhìn thấy những gì người khác không thấy",
            "Cần thời gian - không có sự thật trong khoảnh khắc, cần chu kỳ Mặt Trăng để đạt minh triết"
        ],
        "strategy": {
            "name": "Wait a Lunar Cycle - Chờ Chu Kỳ Mặt Trăng (28-29 ngày)",
            "description": "Đừng quyết định vội, đặc biệt việc lớn. Chờ 28-29 ngày, nói chuyện với nhiều người, ở nhiều môi trường, cảm nhận sự nhất quán theo thời gian và không gian.",
            "practice": "Khi có quyết định lớn, nói chuyện với nhiều người tin cậy khác nhau, ở nhiều nơi khác nhau, trong 28 ngày. Cảm nhận điều gì nhất quán. Môi trường là TẤT CẢ."
        },
        "signature": {"name": "Surprise - Ngạc nhiên", "description": "Khi ở đúng môi trường, với đúng người, cuộc sống kỳ diệu, đầy ngạc nhiên, bạn thấy điều kỳ diệu"},
        "not_self": {"name": "Disappointment - Thất vọng", "description": "Khi môi trường không đúng, với người không đúng, cảm thấy thất vọng về thế giới, về con người. Thất vọng là tín hiệu môi trường sai.", "healing": "Thay đổi môi trường, ở nơi đúng, với người đúng, chờ chu kỳ Mặt Trăng"},
        "work": {"suitable": ["Đánh giá cộng đồng, môi trường, trung gian, phản chiếu", "Vai trò cần thấu cảm, nhìn thấy tổng thể", "Công việc linh hoạt, không gò bó"], "needs": ["Môi trường đúng là TẤT CẢ", "Ngủ, sống, làm việc ở nơi đúng", "Thời gian, không quyết định vội", "Nhiều không gian, thiên nhiên"], "team": "Là người phản chiếu sức khỏe team/cộng đồng, cần môi trường đúng để phản chiếu chính xác"},
        "relationship": {"aura_impact": "Aura lấy mẫu, phản chiếu - người khác thấy chính mình qua bạn", "needs": ["Môi trường đúng", "Thời gian", "Không bị ép quyết định nhanh"], "seeking": "Ngạc nhiên, kỳ diệu, môi trường đúng"},
        "child": {
            "description": "Trẻ Reflector cực kỳ nhạy cảm với môi trường, như bọt biển hút năng lượng xung quanh",
            "wound": "Ở môi trường không đúng, với người không đúng -> Thất vọng sớm, cảm thấy lạc lõng, không thuộc về đâu",
            "advice": ["Môi trường là TẤT CẢ cho con", "Cho con không gian, thiên nhiên, nơi an toàn", "Đừng ép con quyết định nhanh", "Cho con thời gian 28 ngày với quyết định lớn", "Quan sát con phản chiếu môi trường - nếu con thất vọng, kiểm tra môi trường", "Cho con ngủ một mình, không gian riêng"]
        }
    }
}

PROFILE_DEEP_DIVE = {
    "1/3": {"role": "Investigator/Martyr", "angle": "Right Angle - Personal Destiny", "description": "Nghiên cứu thử sai. Cần nền tảng vững chắc, nghiên cứu sâu trước khi hành động. Cuộc đời là thử và sai để tìm ra sự thật. Học qua va chạm. An toàn đến từ kiến thức. 1: Investigator cần an toàn, nền tảng. 3: Martyr thử và sai, thích nghi, hài hước.", "career": "Nghiên cứu, khoa học, chuyên gia, cần nền tảng vững chắc"},
    "1/4": {"role": "Investigator/Opportunist", "angle": "Right Angle", "description": "Nghiên cứu cơ hội. Cần nền tảng vững chắc để chia sẻ với mạng lưới bạn bè. Ảnh hưởng qua người quen. Bạn bè là chìa khóa. 1: nền tảng, 4: mạng lưới.", "career": "Chuyên gia + cộng đồng, ảnh hưởng qua bạn bè"},
    "2/4": {"role": "Hermit/Opportunist", "angle": "Right Angle", "description": "Ẩn sĩ cơ hội. Có tài năng tự nhiên, cần ở một mình để phát triển, rồi được gọi ra qua mạng lưới. Cân bằng giữa ẩn dật và kết nối. 2: tài năng tự nhiên, cần ở một mình. 4: cơ hội qua bạn bè.", "career": "Nghệ sĩ, chuyên gia tài năng tự nhiên được gọi ra"},
    "2/5": {"role": "Hermit/Heretic", "angle": "Right Angle", "description": "Ẩn sĩ dị giáo. Tài năng tự nhiên nhưng bị người khác chiếu rọi kỳ vọng. Cần ở một mình, cẩn thận với sự chiếu rọi. 2: ẩn sĩ tài năng, 5: dị giáo bị kỳ vọng.", "career": "Cố vấn, chuyên gia tài năng tự nhiên nhưng cần biên giới với kỳ vọng"},
    "3/5": {"role": "Martyr/Heretic", "angle": "Right Angle", "description": "Tử vì đạo dị giáo. Cuộc đời thử và sai, va chạm lớn, nhưng để cứu người, mang giải pháp thực tế. Học qua thất bại. 3: thử sai, 5: giải pháp thực tế bị kỳ vọng.", "career": "Thử nghiệm, giải pháp thực tế, cứu người qua trải nghiệm"},
    "3/6": {"role": "Martyr/Role Model", "angle": "Right Angle", "description": "Tử vì đạo hình mẫu. 3 giai đoạn cuộc đời: 0-30 thử sai, 30-50 quan sát trên mái nhà, 50+ làm hình mẫu. Cuộc đời là hành trình trở thành hình mẫu qua thử sai.", "career": "Lãnh đạo qua trải nghiệm, hình mẫu sau 50 tuổi"},
    "4/6": {"role": "Opportunist/Role Model", "angle": "Right Angle", "description": "Cơ hội hình mẫu. Ảnh hưởng qua mạng lưới bạn bè, cần quan sát để trở thành hình mẫu. Bạn bè và quan sát. 4: mạng lưới, 6: quan sát hình mẫu.", "career": "Lãnh đạo cộng đồng, hình mẫu qua mạng lưới"},
    "4/1": {"role": "Opportunist/Investigator", "angle": "Juxtaposition - Fixed Fate (2% - hiếm)", "description": "Cơ hội điều tra. Profile hiếm, định mệnh cố định (Juxtaposition). Không thể bị ảnh hưởng, cần nền tảng vững chắc để ảnh hưởng người khác. Một con đường duy nhất. 4: cơ hội, 1: nền tảng. Định mệnh cố định.", "career": "Chuyên gia một lĩnh vực cố định, không thể bị ảnh hưởng, ảnh hưởng người khác qua nền tảng vững chắc"},
    "5/1": {"role": "Heretic/Investigator", "angle": "Left Angle - Transpersonal Karma", "description": "Dị giáo điều tra. Người mang giải pháp thực tế có nền tảng. Bị kỳ vọng lớn, chiếu rọi. Cần nền tảng vững chắc để đáp ứng kỳ vọng. 5: giải pháp thực tế, 1: nền tảng. Nghiệp với người khác.", "career": "Lãnh đạo, cứu rỗi, giải pháp thực tế có nền tảng, chịu kỳ vọng lớn"},
    "5/2": {"role": "Heretic/Hermit", "angle": "Left Angle", "description": "Dị giáo ẩn sĩ. Giải pháp thực tế + tài năng tự nhiên. Cần ở một mình, cẩn thận với kỳ vọng người khác. 5: dị giáo, 2: ẩn sĩ tài năng.", "career": "Cố vấn giải pháp thực tế + tài năng tự nhiên"},
    "6/2": {"role": "Role Model/Hermit", "angle": "Left Angle", "description": "Hình mẫu ẩn sĩ. 3 giai đoạn, tài năng tự nhiên, quan sát rồi trở thành hình mẫu. Cần ở một mình. 0-30 thử sai, 30-50 trên mái nhà quan sát, 50+ hình mẫu. 6: hình mẫu, 2: ẩn sĩ tài năng.", "career": "Hình mẫu, quan sát, tài năng tự nhiên, tỏa sáng sau 50"},
    "6/3": {"role": "Role Model/Martyr", "angle": "Left Angle", "description": "Hình mẫu tử vì đạo. 3 giai đoạn, thử sai để trở thành hình mẫu. Cuộc đời là hành trình quan sát và thử nghiệm. 6: hình mẫu quan sát, 3: thử sai.", "career": "Hình mẫu qua thử sai, quan sát và trải nghiệm"},
}

def analyze_consultation_general(birth_datetime, name=""):
    """
    Tool tổng quát cho TẤT CẢ Types/Profiles - 5 Types x 12 Profiles = 60 biến thể
    """
    if isinstance(birth_datetime, str):
        # Nếu là string, cần parse
        # Giả sử đã là datetime object
        pass
    
    chart = calculate_hd_chart(birth_datetime) if isinstance(birth_datetime, dt_module.datetime) else birth_datetime
    
    # Lấy thông tin cơ bản
    hd_type = chart["type"]
    profile = chart["profile"]
    authority = chart["authority"]
    definition = chart["definition"]
    
    # Deep dive theo Type
    type_dive = TYPE_DEEP_DIVE.get(hd_type, {})
    
    # Deep dive theo Profile
    profile_dive = PROFILE_DEEP_DIVE.get(profile, {})
    
    # Fear và Love gates (từ advanced tools)
    try:
        fear_analysis = analyze_fear_gates(birth_datetime)
        love_analysis = analyze_love_gates(birth_datetime)
    except:
        fear_analysis = {"total_fear_gates": 0}
        love_analysis = {"total_love_gates": 0}
    
    # Tổng hợp
    result = {
        "name": name,
        "birth_datetime": str(chart["birth_datetime"]),
        "design_datetime": str(chart["design_datetime"]),
        "type": hd_type,
        "profile": profile,
        "authority": authority,
        "strategy": chart["strategy"],
        "definition": definition,
        "incarnation_cross": chart["incarnation_cross"],
        "cross_type": chart["cross_type"],
        "defined_centers": chart["defined_centers"],
        "defined_channels": chart["defined_channels"],
        "all_activated_gates": chart["all_activated_gates"],
        "type_deep_dive": type_dive,
        "profile_deep_dive": profile_dive,
        "fear_gates": {"count": fear_analysis.get("total_fear_gates", 0), "summary": f"{fear_analysis.get('total_fear_gates', 0)} cổng sợ hãi/lo âu/hồi hộp"},
        "love_gates": {"count": love_analysis.get("total_love_gates", 0), "summary": f"{love_analysis.get('total_love_gates', 0)} cổng tình yêu"},
        "consultation_process": {
            "step1_chuẩn_bị": "Thu thập Họ tên, Giờ-Ngày-Tháng-Năm sinh, Nơi sinh chính xác (CÀNG CHÍNH XÁC CÀNG TỐT - sai 5 phút đổi Moon gate, sai 1 giờ đổi Profile)",
            "step2_tính_toán": "Sử dụng tool calculate_human_design_chart với Swiss Ephemeris NASA JPL DE431, độ chính xác <1 arc second. Tính cả Personality (lúc sinh) và Design (88° Sun trước sinh)",
            "step3_phân_tích": "Theo thứ tự ưu tiên: 1. Type + Strategy + Authority (80% giá trị) 2. Centers (defined/open) 3. Channels (tài năng cố định) 4. Gates (cổng treo) 5. Profile (vai trò) 6. Cross (mục đích) 7. Definition",
            "step4_thực_hành": "Hướng dẫn thử nghiệm 7 ngày với Strategy/Authority, quan sát Centers mở, deconditioning 7 năm"
        },
        "buổi_đọc_chuyên_nghiệp": {
            "tổng_thời_gian": "1-2 giờ",
            "cấu_trúc": [
                "Mở đầu (10 phút): Giải thích Human Design là gì, không phải bói toán, là thử nghiệm - 'Đừng tin, hãy thử nghiệm' - Ra Uru Hu",
                "Type + Strategy + Authority (40 phút): Quan trọng nhất, 80% giá trị",
                "Centers (20 phút): Defined/Open, Not-Self, trí tuệ",
                "Profile (10 phút): Vai trò cuộc đời",
                "Channels/Gates nổi bật (20 phút): Tài năng cố định + cổng treo",
                "Incarnation Cross (10 phút): Mục đích sống",
                "Hỏi đáp + Thực hành (20 phút): Hành động cụ thể 7 ngày"
            ],
            "kết_thúc": "Luôn kết thúc bằng: 'Hãy thử nghiệm 7 ngày với Strategy/Authority và quan sát'"
        },
        "nguyên_tắc_đạo_đức": [
            "Hiểu mình - Sống là mình",
            "Human Design là thử nghiệm (Experiment), không phải niềm tin mù quáng",
            "Khuyến khích khách hàng tự chứng thực Strategy và Authority trong đời sống thực tế",
            "Không dùng để phán xét, dán nhãn",
            "Không thay thế y tế, tâm lý chuyên nghiệp",
            "Tôn trọng Type: Đừng bảo Generator 'hãy khởi xướng', đừng bảo Projector 'hãy làm việc chăm chỉ hơn'",
            "Không có chart xấu - mỗi thiết kế có mục đích",
            "Tâm trí (Mind) KHÔNG BAO GIỜ là Authority - Mind để đo lường, không phải ra quyết định"
        ],
        "lộ_trình_thực_hành": {
            "7_ngày": f"Thử nghiệm Strategy: {chart['strategy']} + Authority: {authority}",
            "7_tháng": "Quan sát Centers mở - nơi bạn học trí tuệ, không phải ra quyết định",
            "7_năm": "Deconditioning - Giải điều kiện hóa, tế bào cơ thể thay mới hoàn toàn (chu kỳ Uranus)"
        },
        "áp_dụng_cho": "100% dân số - 5 Types x 12 Profiles = 60 biến thể. Tool này tổng quát cho tất cả, với deep dive chi tiết cho từng Type/Profile cụ thể."
    }
    
    return result

def format_consultation_report(consultation_data):
    """Format báo cáo tham vấn tổng quát"""
    chart_type = consultation_data["type"]
    profile = consultation_data["profile"]
    
    type_dive = consultation_data.get("type_deep_dive", {})
    profile_dive = consultation_data.get("profile_deep_dive", {})
    
    lines = []
    lines.append(f"# BÁO CÁO THAM VẤN TỔNG QUÁT HUMAN DESIGN - {consultation_data.get('name','')} - ÁP DỤNG CHO TẤT CẢ TYPES/PROFILES")
    lines.append(f"**Ngày sinh:** {consultation_data['birth_datetime']} UTC | **Design:** {consultation_data['design_datetime']} UTC")
    lines.append(f"**Type:** {chart_type} | **Profile:** {profile} | **Authority:** {consultation_data['authority']} | **Definition:** {consultation_data['definition']}")
    lines.append(f"**Cross:** {consultation_data['incarnation_cross']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Type deep dive
    lines.append(f"## 1. TYPE: {chart_type} - DEEP DIVE")
    lines.append(f"**Aura:** {type_dive.get('aura','')}")
    lines.append("")
    lines.append(f"**Tâm lý:**")
    for psy in type_dive.get('psychology', []):
        lines.append(f"- {psy}")
    lines.append("")
    lines.append(f"**Strategy:** {type_dive.get('strategy',{}).get('name','')} - {type_dive.get('strategy',{}).get('description','')}")
    lines.append(f"**Thực hành:** {type_dive.get('strategy',{}).get('practice','')}")
    lines.append("")
    lines.append(f"**Signature:** {type_dive.get('signature',{}).get('name','')} - {type_dive.get('signature',{}).get('description','')}")
    lines.append("")
    lines.append(f"**Not-Self:** {type_dive.get('not_self',{}).get('name','')} - {type_dive.get('not_self',{}).get('description','')}")
    lines.append(f"**Chữa lành:** {type_dive.get('not_self',{}).get('healing','')}")
    lines.append("")
    
    # Profile deep dive
    lines.append(f"## 2. PROFILE: {profile} - {profile_dive.get('role','')}")
    lines.append(f"**Góc độ:** {profile_dive.get('angle','')}")
    lines.append(f"**Mô tả:** {profile_dive.get('description','')}")
    lines.append(f"**Nghề nghiệp phù hợp:** {profile_dive.get('career','')}")
    lines.append("")
    
    # Centers, Channels
    lines.append(f"## 3. CENTERS & CHANNELS")
    lines.append(f"**Defined Centers ({len(consultation_data['defined_centers'])}):** {', '.join(consultation_data['defined_centers'])}")
    lines.append(f"**Defined Channels ({len(consultation_data['defined_channels'])}):** {consultation_data['defined_channels']}")
    lines.append(f"**All Gates ({len(consultation_data['all_activated_gates'])}):** {consultation_data['all_activated_gates']}")
    lines.append(f"**Fear Gates:** {consultation_data['fear_gates']['summary']}")
    lines.append(f"**Love Gates:** {consultation_data['love_gates']['summary']}")
    lines.append("")
    
    # Consultation process
    lines.append(f"## 4. QUY TRÌNH THAM VẤN CHUYÊN NGHIỆP (Áp dụng cho TẤT CẢ Types/Profiles)")
    for step, desc in consultation_data["consultation_process"].items():
        lines.append(f"- **{step}:** {desc}")
    lines.append("")
    lines.append(f"**Buổi đọc chuyên nghiệp {consultation_data['buổi_đọc_chuyên_nghiệp']['tổng_thời_gian']}:**")
    for item in consultation_data["buổi_đọc_chuyên_nghiệp"]["cấu_trúc"]:
        lines.append(f"- {item}")
    lines.append(f"- **Kết thúc:** {consultation_data['buổi_đọc_chuyên_nghiệp']['kết_thúc']}")
    lines.append("")
    
    # Ethics
    lines.append(f"## 5. NGUYÊN TẮC ĐẠO ĐỨC")
    for ethic in consultation_data["nguyên_tắc_đạo_đức"]:
        lines.append(f"- {ethic}")
    lines.append("")
    
    # Practice roadmap
    lines.append(f"## 6. LỘ TRÌNH THỰC HÀNH")
    for period, action in consultation_data["lộ_trình_thực_hành"].items():
        lines.append(f"- **{period}:** {action}")
    lines.append("")
    
    # Work & Relationship & Child specific to Type
    lines.append(f"## 7. CÔNG VIỆC - MỐI QUAN HỆ - TRẺ EM (Theo Type {chart_type})")
    lines.append(f"**Công việc phù hợp:** {type_dive.get('work',{}).get('suitable',[])}")
    lines.append(f"**Cần:** {type_dive.get('work',{}).get('needs',[])}")
    lines.append(f"**Team:** {type_dive.get('work',{}).get('team','')}")
    lines.append("")
    lines.append(f"**Mối quan hệ:** Aura {type_dive.get('relationship',{}).get('aura_impact','')} - Cần {type_dive.get('relationship',{}).get('needs',[])} - Tìm kiếm {type_dive.get('relationship',{}).get('seeking','')}")
    lines.append("")
    if "child" in type_dive:
        lines.append(f"**Trẻ em {chart_type}:** {type_dive['child']['description']}")
        lines.append(f"**Vết thương:** {type_dive['child']['wound']}")
        lines.append(f"**Lời khuyên phụ huynh:**")
        for adv in type_dive['child']['advice']:
            lines.append(f"- {adv}")
    lines.append("")
    
    lines.append(f"## 8. TỔNG KẾT")
    lines.append(f"Tool này áp dụng cho {consultation_data['áp_dụng_cho']}")
    lines.append(f"Bạn là {chart_type} {profile} - {type_dive.get('signature',{}).get('name','')} khi sống đúng, {type_dive.get('not_self',{}).get('name','')} khi sống sai.")
    lines.append(f"Hãy thử nghiệm 7 ngày với Strategy: {consultation_data['strategy']} và Authority: {consultation_data['authority']}")
    lines.append("")
    lines.append("> \"Đừng tin, hãy thử nghiệm\" - Ra Uru Hu")
    lines.append("> \"Hiểu mình - Sống là mình\"")
    
    return "\n".join(lines)

# Test
if __name__ == "__main__":
    dt = datetime(1990, 5, 15, 1, 30)
    data = analyze_consultation_general(dt, name="Test User")
    print(format_consultation_report(data)[:5000])

// Game "Đúng Thiết Kế" (G2) — nội dung theme, phong cách, copy đối chiếu.
// Thêm theme mới = thêm 1 object GameTheme. Mỗi slot có thể có nhiều biến thể
// tình huống (xoay vòng mỗi lượt chơi để không nhàm).

export type StyleId = "khoi_xuong" | "kien_tao" | "dan_duong" | "tam_guong";
export type DecisionId = "truc_giac" | "cam_xuc" | "logic" | "hoi_han";

export interface GameOption {
  id: string;
  label: string;
  points: Record<StyleId, number>;
  /** -1 (năng lượng theo đợt) .. +1 (pin bền bỉ) */
  energy: number;
  /** -1 (thích chờ thời) .. +1 (thích lao ngay) */
  pace: number;
  decision?: DecisionId;
}

export interface GameScenario {
  id: string;
  title: string;
  situation: string;
  options: GameOption[];
}

/** 1 slot = 1 tình huống trong lượt chơi, chọn ngẫu nhiên 1 biến thể. */
export interface GameScenarioSlot {
  id: string;
  variants: GameScenario[];
}

export interface GameTheme {
  slug: string;
  name: string;
  entryLabel: string;
  entryDesc: string;
  icon: string;
  intro: string;
  bridge: string;
  scenarios: GameScenarioSlot[];
}

export interface BehaviorStyle {
  id: StyleId;
  name: string;
  icon: string;
  tagline: string;
  desc: string;
  strength: string;
  blindspot: string;
}

export const STYLES: Record<StyleId, BehaviorStyle> = {
  khoi_xuong: {
    id: "khoi_xuong",
    name: "Người Khởi Xướng",
    icon: "🔥",
    tagline: "Nghĩ là làm — cả thế giới đi theo sau.",
    desc: "Bạn có xu hướng mở đường: quyết nhanh, hành động trước, ghét chờ đợi và ghét bị kiểm soát. Khi có lửa, không ai cản nổi bạn.",
    strength: "Bật nắp được những việc người khác chần chừ cả năm.",
    blindspot: "Lao đi khi chưa đúng lúc sẽ gặp toàn tường — và bạn gọi đó là số nhọ.",
  },
  kien_tao: {
    id: "kien_tao",
    name: "Người Kiến Tạo",
    icon: "⚒️",
    tagline: "Đúng việc thì cày quên ăn — sai việc thì kiệt pin.",
    desc: "Bạn là cỗ máy bền bỉ: một khi bắt đúng nhịp việc mình yêu, năng lượng tuôn không ngừng. Nhưng ép mình làm việc chán thì pin tụt nhanh hơn ai hết.",
    strength: "Sức cày và sự dẻo dai mà người khác phải ghen tị.",
    blindspot: "Nhận việc vì nể nang rồi kẹt cứng trong chán nản.",
  },
  dan_duong: {
    id: "dan_duong",
    name: "Người Dẫn Đường",
    icon: "🦉",
    tagline: "Không cày nhiều — nhưng nhìn ra điều cả đội bỏ sót.",
    desc: "Bạn mạnh ở tầm nhìn: lùi một bước là thấy điểm nghẽn, thấy ai hợp việc gì. Năng lượng của bạn dành cho quan sát và dẫn dắt, không phải cày cuốc.",
    strength: "Một câu chỉ điểm đúng lúc đáng giá cả tuần cày của người khác.",
    blindspot: "Cố cày như máy để chứng minh mình — rồi sập nguồn trong cay đắng.",
  },
  tam_guong: {
    id: "tam_guong",
    name: "Tấm Gương",
    icon: "🪞",
    tagline: "Nhạy với mọi rung động quanh mình.",
    desc: "Bạn hấp thụ môi trường cực mạnh: ở cạnh ai, bạn cảm được nhịp của người đó. Đây là món quà thấu cảm hiếm — nếu bạn biết đâu là mình, đâu là người ta.",
    strength: "Đọc vị không khí và lòng người nhanh hơn mọi lý lẽ.",
    blindspot: "Sống theo tiêu chuẩn của người khác mà tưởng là ý mình.",
  },
};

export const DECISIONS: Record<DecisionId, { name: string; desc: string }> = {
  truc_giac: { name: "Trực giác tức thì", desc: "Linh tính mách sao làm vậy." },
  cam_xuc: { name: "Để cảm xúc lắng rồi quyết", desc: "Ngủ qua đêm mới biết mình thật sự muốn gì." },
  logic: { name: "Phân tích kỹ rồi quyết", desc: "Bảng so sánh thiệt hơn trước, cảm xúc sau." },
  hoi_han: { name: "Hỏi han rồi quyết", desc: "Nghe nhiều tai rồi mới dám chốt." },
};

const S1A = {
  id: "sang-thu-hai",
  title: "Sáng thứ Hai",
  situation:
    "6h30 sáng. Cả thành phố đã hùng hục lao đi, còn bạn nằm nhìn trần nhà, cơ thể nặng như đeo chì. Điều gì diễn ra trong đầu bạn?",
  options: [
    {
      id: "day-lao",
      label: "Dậy! Kỷ luật là sức mạnh. Lao đi rồi sẽ quen.",
      points: { khoi_xuong: 2, kien_tao: 1, dan_duong: 0, tam_guong: 0 },
      energy: 1,
      pace: 1,
    },
    {
      id: "toi-loi",
      label: "Lại thấy tội lỗi… Sao mình không được như người ta?",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
      energy: -1,
      pace: 0,
    },
    {
      id: "xem-viec",
      label: "Để xem hôm nay có việc gì đáng làm đã. Không thì nằm thêm.",
      points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 1, tam_guong: 0 },
      energy: 0,
      pace: -1,
    },
    {
      id: "nhin-tuan",
      label: "Nằm thêm 5 phút để nhìn lại: tuần này cái gì mới thật sự quan trọng?",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
      energy: -1,
      pace: -1,
    },
  ],
};

const S1B = {
  id: "toi-chu-nhat",
  title: "Tối Chủ Nhật",
  situation:
    "Tối Chủ Nhật, mai đi làm. Nhóm chat công việc đã nổ tin nhắn. Bạn sẽ làm gì với cái điện thoại trên tay?",
  options: [
    {
      id: "mo-may",
      label: "Mở máy xử lý luôn cho gọn, tuần mới nhẹ đầu.",
      points: { khoi_xuong: 2, kien_tao: 1, dan_duong: 0, tam_guong: 0 },
      energy: 1,
      pace: 1,
    },
    {
      id: "thap-thom",
      label: "Đọc mà thấp thỏm cả tối, chẳng dám tắt máy.",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
      energy: -1,
      pace: 0,
    },
    {
      id: "luot-qua",
      label: "Lướt qua, việc nào gọi tên mình mới động tay.",
      points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 1, tam_guong: 0 },
      energy: 0,
      pace: -1,
    },
    {
      id: "note-3viec",
      label: "Gác máy, ngồi note lại 3 việc quan trọng nhất tuần.",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
      energy: -1,
      pace: -1,
    },
  ],
};

const S2A = {
  id: "loi-nho-va",
  title: "Lời nhờ vả",
  situation:
    "Bạn đang ngập đầu việc của mình. Đồng nghiệp thân chạy sang: “Cứu tớ vụ này với, gấp lắm!” Phản xạ đầu tiên của bạn là gì?",
  options: [
    {
      id: "nhan-ngay",
      label: "“Ừ, để đấy tớ làm!” — miệng nói trước, não tính sau.",
      points: { khoi_xuong: 0, kien_tao: 2, dan_duong: 0, tam_guong: 0 },
      energy: 1,
      pace: 1,
    },
    {
      id: "tu-choi",
      label: "“Không được, việc tớ còn chưa xong.” — từ chối thẳng, không day dứt.",
      points: { khoi_xuong: 2, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
      energy: 0,
      pace: 1,
    },
    {
      id: "soi-viec",
      label: "“Để tớ xem nào… vụ này có thật sự cần tớ không, hay ai làm cũng được?”",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
      energy: 0,
      pace: -1,
    },
    {
      id: "so-buon",
      label: "Nhận lời vì sợ họ buồn, rồi về nhà ấm ức cả tối.",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
      energy: -1,
      pace: 0,
    },
  ],
};

const S3A = {
  id: "co-hoi-chop",
  title: "Cơ hội chớp nhoáng",
  situation:
    "Một cơ hội hiếm (việc mới, deal đầu tư, chuyến đi) xuất hiện. Hạn chót: 24 giờ. Bạn sẽ quyết thế nào?",
  options: [
    {
      id: "chot-linh",
      label: "Chốt ngay theo linh tính. Đúng sai tính sau.",
      points: { khoi_xuong: 1, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
      energy: 0,
      pace: 1,
      decision: "truc_giac",
    },
    {
      id: "de-mai",
      label: "Để mai trả lời. Cảm xúc lắng xuống mới biết mình thật sự muốn gì.",
      points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
      energy: 0,
      pace: -1,
      decision: "cam_xuc",
    },
    {
      id: "lap-bang",
      label: "Lập bảng so sánh thiệt hơn rồi mới quyết.",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 1, tam_guong: 0 },
      energy: 0,
      pace: -1,
      decision: "logic",
    },
    {
      id: "hoi-nguoi",
      label: "Gọi ngay cho 2–3 người thân cận nhất để hỏi ý.",
      points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 1, tam_guong: 1 },
      energy: 0,
      pace: -1,
      decision: "hoi_han",
    },
  ],
};

const S3B = {
  id: "loi-moi-viec",
  title: "Lời mời việc",
  situation:
    "Công ty trong mơ mời bạn phỏng vấn, nhưng phải trả lời trong hôm nay. Tay bạn run run trên nút gửi. Bạn sẽ?",
  options: [
    {
      id: "nhan-linh",
      label: "Nhận lời ngay, linh tính bảo đây là chỗ của mình.",
      points: { khoi_xuong: 1, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
      energy: 0,
      pace: 1,
      decision: "truc_giac",
    },
    {
      id: "toi-tra-loi",
      label: "Để tối trả lời, cần cảm nhận cho chắc đã.",
      points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
      energy: 0,
      pace: -1,
      decision: "cam_xuc",
    },
    {
      id: "so-luong",
      label: "So lương, phúc lợi, lộ trình rồi mới quyết.",
      points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 1, tam_guong: 0 },
      energy: 0,
      pace: -1,
      decision: "logic",
    },
    {
      id: "hoi-nguoi-cu",
      label: "Hỏi người đã làm ở đó trước đã.",
      points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 1, tam_guong: 1 },
      energy: 0,
      pace: -1,
      decision: "hoi_han",
    },
  ],
};

export const THEME_NGUOC_DONG: GameTheme = {
  slug: "nguoc-dong",
  name: "Thế Giới Ngược Dòng",
  entryLabel: "Soi lại chính mình",
  entryDesc: "Bạn thực sự lười biếng, hay đang sống theo tiêu chuẩn của người khác?",
  icon: "🧠",
  intro:
    "3 khoảnh khắc đời thường. Không có đáp án đúng — chỉ có phản xạ thật của bạn. Chọn ngay lựa chọn đầu tiên nảy ra trong đầu.",
  bridge:
    "Bản phác thảo hành vi đã xong. Giờ nhập ngày giờ sinh để hệ thống tính thiết kế gốc của bạn — và xem hai bản này khớp nhau bao nhiêu phần trăm.",
  scenarios: [
    { id: "slot-1", variants: [S1A, S1B] },
    { id: "slot-2", variants: [S2A] },
    { id: "slot-3", variants: [S3A, S3B] },
  ],
};

export const THEME_THUONG_VU: GameTheme = {
  slug: "thuong-vu",
  name: "Thương Vụ Sinh Tử",
  entryLabel: "Thử thách Sự nghiệp",
  entryDesc: "Bạn là Người Cày Dự Án hay Kẻ Thao Túng Cuộc Chơi?",
  icon: "💼",
  intro:
    "Bạn bị ném vào một dự án trên bờ vực. 3 quyết định cân não, không có đáp án đúng — chỉ có bản năng làm việc thật của bạn.",
  bridge:
    "Phong cách làm việc của bạn đã lộ diện. Nhập ngày giờ sinh để xem thiết kế gốc nói gì về con đường sự nghiệp của bạn.",
  scenarios: [
    {
      id: "slot-1",
      variants: [
        {
          id: "du-an-nghen",
          title: "Dự án nghẽn",
          situation:
            "Dự án 2 tỷ đang nghẽn đúng khâu của bạn, cả đội nhìn bạn. Deadline còn 48 giờ. Bạn sẽ?",
          options: [
            {
              id: "cay-xuyen-dem",
              label: "Xắn tay cày xuyên đêm, sai đâu sửa đấy.",
              points: { khoi_xuong: 0, kien_tao: 2, dan_duong: 0, tam_guong: 0 },
              energy: 1,
              pace: 1,
            },
            {
              id: "lui-nua-ngay",
              label: "Lùi lại nửa ngày: tìm đúng điểm nghẽn rồi chia việc lại.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
              energy: 0,
              pace: -1,
            },
            {
              id: "dam-phan",
              label: "Gọi sếp và khách, đàm phán lại phạm vi và deadline.",
              points: { khoi_xuong: 2, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
              energy: 0,
              pace: 1,
            },
            {
              id: "hoi-ca-doi",
              label: "Hỏi cả đội xem ai thấy sao, rồi theo số đông.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
              energy: 0,
              pace: -1,
            },
          ],
        },
      ],
    },
    {
      id: "slot-2",
      variants: [
        {
          id: "deal-24h",
          title: "Deal 24 giờ",
          situation:
            "Cơ hội đầu tư lợi nhuận khủng, hạn chót 24h. Tài liệu dày 50 trang bạn chưa đọc hết. Phản xạ của bạn?",
          options: [
            {
              id: "chot-giac-quan",
              label: "Chốt luôn. Giác quan bảo đúng là đúng.",
              points: { khoi_xuong: 1, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
              energy: 0,
              pace: 1,
              decision: "truc_giac",
            },
            {
              id: "xin-hoan",
              label: "Xin hoãn. Ngủ một đêm cho cảm xúc nguội rồi tính.",
              points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
              energy: 0,
              pace: -1,
              decision: "cam_xuc",
            },
            {
              id: "cay-50-trang",
              label: "Cày hết 50 trang và bảng số liệu rồi mới quyết.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 1, tam_guong: 0 },
              energy: 0,
              pace: -1,
              decision: "logic",
            },
            {
              id: "goi-nguoi-sanh",
              label: "Gọi 2 người sành nhất hỏi ý kiến.",
              points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
              energy: 0,
              pace: -1,
              decision: "hoi_han",
            },
          ],
        },
      ],
    },
    {
      id: "slot-3",
      variants: [
        {
          id: "ap-luc-toi",
          title: "9 giờ tối",
          situation:
            "9h tối, bạn đã kiệt sức. Sếp nhắn: thêm một việc gấp, sáng mai phải có. Bạn phản ứng thế nào?",
          options: [
            {
              id: "cay-tiep",
              label: "Nhận và cày tiếp. Việc là trên hết.",
              points: { khoi_xuong: 0, kien_tao: 2, dan_duong: 0, tam_guong: 0 },
              energy: 1,
              pace: 1,
            },
            {
              id: "tu-choi-thang",
              label: "Từ chối thẳng: quá giờ rồi, mai tính.",
              points: { khoi_xuong: 2, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
              energy: 0,
              pace: 1,
            },
            {
              id: "nhan-am-uc",
              label: "Nhận vì sợ mất lòng, rồi ấm ức cả đêm.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
              energy: -1,
              pace: 0,
            },
            {
              id: "hoi-cach-doi",
              label: "Hỏi lại: việc này có thật sự cần tối nay không, hay dời được?",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
              energy: 0,
              pace: -1,
            },
          ],
        },
      ],
    },
  ],
};

export const THEME_LINH_THU: GameTheme = {
  slug: "linh-thu",
  name: "Khu Rừng Linh Thú",
  entryLabel: "Khám phá Linh thú",
  entryDesc: "Linh thú năng lượng nào đang dẫn lối cho bạn?",
  icon: "🔮",
  intro:
    "Bạn lạc vào khu rừng thần thoại, nơi linh hồn mỗi người hóa thành một sinh vật. Đi qua 3 trạm, rừng sẽ cho bạn thấy hình dạng thật của mình.",
  bridge:
    "Linh thú của bạn đã lộ diện. Nhập ngày giờ sinh để xem tần số gốc đằng sau linh thú đó là gì.",
  scenarios: [
    {
      id: "slot-1",
      variants: [
        {
          id: "nga-ba-rung",
          title: "Ngã ba rừng",
          situation:
            "Rừng chia 3 lối: đường mòn đông dấu chân, đường rậm ít ai đi, và tảng đá cao nhìn được toàn cảnh. Bạn chọn?",
          options: [
            {
              id: "duong-ram",
              label: "Đường rậm — tự mở lối riêng.",
              points: { khoi_xuong: 2, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
              energy: 1,
              pace: 1,
            },
            {
              id: "duong-mon",
              label: "Đường mòn — đi cùng bầy cho chắc.",
              points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
              energy: 0,
              pace: 0,
            },
            {
              id: "leo-da",
              label: "Leo tảng đá quan sát trước đã.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
              energy: 0,
              pace: -1,
            },
            {
              id: "dung-cam",
              label: "Đứng yên cảm nhận xem lối nào “gọi” mình.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
              energy: -1,
              pace: -1,
            },
          ],
        },
      ],
    },
    {
      id: "slot-2",
      variants: [
        {
          id: "tieng-goi-bay",
          title: "Tiếng gọi bầy đàn",
          situation:
            "Bầy thú hú gọi bạn nhập đàn săn đêm, nhưng cơ thể bạn rã rời. Trăng đã lên cao. Bạn sẽ?",
          options: [
            {
              id: "giu-loi",
              label: "Đi! Đã hứa với bầy thì phải giữ lời.",
              points: { khoi_xuong: 0, kien_tao: 2, dan_duong: 0, tam_guong: 0 },
              energy: 1,
              pace: 0,
            },
            {
              id: "co-the-minh",
              label: "Không đi. Cơ thể mình, mình quyết.",
              points: { khoi_xuong: 2, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
              energy: 0,
              pace: 1,
            },
            {
              id: "quan-sat-san",
              label: "Đi theo nhưng chỉ quan sát, không săn.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 },
              energy: 0,
              pace: -1,
            },
            {
              id: "so-bo-lai",
              label: "Đi vì sợ bị bỏ lại, dù chẳng muốn.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 },
              energy: -1,
              pace: 0,
            },
          ],
        },
      ],
    },
    {
      id: "slot-3",
      variants: [
        {
          id: "trai-cam",
          title: "Trái cấm",
          situation:
            "Linh vật rừng đưa bạn một trái lạ: ăn vào sẽ thấy tương lai 1 năm tới, nhưng phải đánh đổi một thói quen cũ. Bạn quyết thế nào?",
          options: [
            {
              id: "an-ngay",
              label: "Ăn ngay. Thấy trước tính sau.",
              points: { khoi_xuong: 1, kien_tao: 0, dan_duong: 0, tam_guong: 0 },
              energy: 0,
              pace: 1,
              decision: "truc_giac",
            },
            {
              id: "de-mai-ngu",
              label: "Để mai. Đêm nay ngủ xem giấc mơ bảo gì.",
              points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
              energy: 0,
              pace: -1,
              decision: "cam_xuc",
            },
            {
              id: "hoi-dieu-kien",
              label: "Hỏi linh vật cho rõ điều kiện đã.",
              points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 1, tam_guong: 0 },
              energy: 0,
              pace: -1,
              decision: "logic",
            },
            {
              id: "ru-bay",
              label: "Rủ cả bầy cùng ăn cho vui.",
              points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 },
              energy: 0,
              pace: 0,
              decision: "hoi_han",
            },
          ],
        },
      ],
    },
  ],
};

export const THEMES: Record<string, GameTheme> = {
  [THEME_NGUOC_DONG.slug]: THEME_NGUOC_DONG,
  [THEME_THUONG_VU.slug]: THEME_THUONG_VU,
  [THEME_LINH_THU.slug]: THEME_LINH_THU,
};

/** Theme chưa mở — hiện thẻ khóa để tạo mong chờ + đo nhu cầu. */
export const LOCKED_THEMES: { name: string; desc: string; icon: string }[] = [];

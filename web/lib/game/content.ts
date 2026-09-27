// Game "Đúng Thiết Kế" (G1) — nội dung theme, phong cách, copy đối chiếu.
// Thêm theme mới = thêm 1 object GameTheme, không đụng code.

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

export interface GameTheme {
  slug: string;
  name: string;
  entryLabel: string;
  entryDesc: string;
  icon: string;
  intro: string;
  bridge: string;
  scenarios: GameScenario[];
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

export const THEME_NGUOC_DONG: GameTheme = {
  slug: "nguoc-dong",
  name: "Thế Giới Ngược Dòng",
  entryLabel: "Soi lại chính mình",
  entryDesc: "Bạn thực sự lười biếng, hay đang sống theo tiêu chuẩn của người khác?",
  icon: "🧠",
  intro: "3 khoảnh khắc đời thường. Không có đáp án đúng — chỉ có phản xạ thật của bạn. Chọn ngay lựa chọn đầu tiên nảy ra trong đầu.",
  bridge: "Bản phác thảo hành vi đã xong. Giờ nhập ngày giờ sinh để hệ thống tính thiết kế gốc của bạn — và xem hai bản này khớp nhau bao nhiêu phần trăm.",
  scenarios: [
    {
      id: "sang-thu-hai",
      title: "Sáng thứ Hai",
      situation: "6h30 sáng. Cả thành phố đã hùng hục lao đi, còn bạn nằm nhìn trần nhà, cơ thể nặng như đeo chì. Điều gì diễn ra trong đầu bạn?",
      options: [
        {
          id: "day-lao", label: "Dậy! Kỷ luật là sức mạnh. Lao đi rồi sẽ quen.",
          points: { khoi_xuong: 2, kien_tao: 1, dan_duong: 0, tam_guong: 0 }, energy: 1, pace: 1,
        },
        {
          id: "toi-loi", label: "Lại thấy tội lỗi… Sao mình không được như người ta?",
          points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 }, energy: -1, pace: 0,
        },
        {
          id: "xem-viec", label: "Để xem hôm nay có việc gì đáng làm đã. Không thì nằm thêm.",
          points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 1, tam_guong: 0 }, energy: 0, pace: -1,
        },
        {
          id: "nhin-tuan", label: "Nằm thêm 5 phút để nhìn lại: tuần này cái gì mới thật sự quan trọng?",
          points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 }, energy: -1, pace: -1,
        },
      ],
    },
    {
      id: "loi-nho-va",
      title: "Lời nhờ vả",
      situation: "Bạn đang ngập đầu việc của mình. Đồng nghiệp thân chạy sang: “Cứu tớ vụ này với, gấp lắm!” Phản xạ đầu tiên của bạn là gì?",
      options: [
        {
          id: "nhan-ngay", label: "“Ừ, để đấy tớ làm!” — miệng nói trước, não tính sau.",
          points: { khoi_xuong: 0, kien_tao: 2, dan_duong: 0, tam_guong: 0 }, energy: 1, pace: 1,
        },
        {
          id: "tu-choi", label: "“Không được, việc tớ còn chưa xong.” — từ chối thẳng, không day dứt.",
          points: { khoi_xuong: 2, kien_tao: 0, dan_duong: 0, tam_guong: 0 }, energy: 0, pace: 1,
        },
        {
          id: "soi-viec", label: "“Để tớ xem nào… vụ này có thật sự cần tớ không, hay ai làm cũng được?”",
          points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 2, tam_guong: 0 }, energy: 0, pace: -1,
        },
        {
          id: "so-buon", label: "Nhận lời vì sợ họ buồn, rồi về nhà ấm ức cả tối.",
          points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 0, tam_guong: 2 }, energy: -1, pace: 0,
        },
      ],
    },
    {
      id: "co-hoi-chop",
      title: "Cơ hội chớp nhoáng",
      situation: "Một cơ hội hiếm (việc mới, deal đầu tư, chuyến đi) xuất hiện. Hạn chót: 24 giờ. Bạn sẽ quyết thế nào?",
      options: [
        {
          id: "chot-linh", label: "Chốt ngay theo linh tính. Đúng sai tính sau.",
          points: { khoi_xuong: 1, kien_tao: 0, dan_duong: 0, tam_guong: 0 }, energy: 0, pace: 1,
          decision: "truc_giac",
        },
        {
          id: "de-mai", label: "Để mai trả lời. Cảm xúc lắng xuống mới biết mình thật sự muốn gì.",
          points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 0, tam_guong: 1 }, energy: 0, pace: -1,
          decision: "cam_xuc",
        },
        {
          id: "lap-bang", label: "Lập bảng so sánh thiệt hơn rồi mới quyết.",
          points: { khoi_xuong: 0, kien_tao: 0, dan_duong: 1, tam_guong: 0 }, energy: 0, pace: -1,
          decision: "logic",
        },
        {
          id: "hoi-nguoi", label: "Gọi ngay cho 2–3 người thân cận nhất để hỏi ý.",
          points: { khoi_xuong: 0, kien_tao: 1, dan_duong: 1, tam_guong: 1 }, energy: 0, pace: -1,
          decision: "hoi_han",
        },
      ],
    },
  ],
};

export const THEMES: Record<string, GameTheme> = {
  [THEME_NGUOC_DONG.slug]: THEME_NGUOC_DONG,
};

/** Theme chưa mở — hiện thẻ khóa để tạo mong chờ + đo nhu cầu. */
export const LOCKED_THEMES: { name: string; desc: string; icon: string }[] = [
  {
    name: "Thương Vụ Sinh Tử",
    desc: "Bạn là Người Cày Dự Án hay Kẻ Thao Túng Cuộc Chơi?",
    icon: "💼",
  },
  {
    name: "Khu Rừng Linh Thú",
    desc: "Linh thú năng lượng nào đang dẫn lối cho bạn?",
    icon: "🔮",
  },
];

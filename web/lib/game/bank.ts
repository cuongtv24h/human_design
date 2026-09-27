// Kho câu hỏi game: mỗi concept ~100 câu, mỗi lượt rút ngẫu nhiên 16 câu.
// Mỗi câu có đúng 4 đáp án, mỗi đáp án cộng điểm cho 1 phong cách (cân bằng tuyệt đối).
import type { StyleId } from "./content";
import { BANK_LINH_THU } from "./bank-linh-thu";
import { BANK_NGUOC_DONG } from "./bank-nguoc-dong";
import { BANK_THUONG_VU } from "./bank-thuong-vu";

export interface BankOption {
  /** nội dung đáp án */
  t: string;
  /** phong cách đáp án này cộng điểm */
  s: StyleId;
}

export interface BankQuestion {
  id: string;
  title: string;
  /** tình huống (1–2 câu) */
  sit: string;
  opts: [BankOption, BankOption, BankOption, BankOption];
}

export const BANKS: Record<string, BankQuestion[]> = {
  "nguoc-dong": BANK_NGUOC_DONG,
  "thuong-vu": BANK_THUONG_VU,
  "linh-thu": BANK_LINH_THU,
};

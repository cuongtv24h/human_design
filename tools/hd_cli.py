#!/usr/bin/env python3
"""
Human Design CLI - Công cụ dòng lệnh để tính toán và phân tích Human Design
Sử dụng: python hd_cli.py --date 1990-05-15 --time 08:30 --timezone +07:00
"""

import argparse
from datetime import datetime, timedelta, timezone
import sys
import os

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(__file__))

from hd_calculator import calculate_hd_chart, format_chart_text
from hd_analyzer import analyze_chart

def parse_datetime(date_str, time_str, tz_str):
    """Parse ngày giờ và timezone"""
    # date: YYYY-MM-DD, time: HH:MM, tz: +07:00 hoặc Asia/Bangkok
    dt_str = f"{date_str} {time_str}"
    try:
        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except:
        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    # Xử lý timezone
    if tz_str.startswith("+") or tz_str.startswith("-"):
        # +07:00
        sign = 1 if tz_str[0] == "+" else -1
        hours = int(tz_str[1:3])
        mins = int(tz_str[4:6]) if len(tz_str) > 3 else 0
        offset = timedelta(hours=sign*hours, minutes=sign*mins)
        tz = timezone(offset)
        dt_aware = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        # Mặc định +07:00 cho VN
        offset = timedelta(hours=7)
        tz = timezone(offset)
        dt_aware = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(timezone.utc).replace(tzinfo=None)
    
    return dt_utc, dt_naive, tz_str

def main():
    parser = argparse.ArgumentParser(description="Human Design Calculator - Tính toán bản đồ Human Design chính xác")
    parser.add_argument("--date", required=True, help="Ngày sinh YYYY-MM-DD (ví dụ: 1990-05-15)")
    parser.add_argument("--time", required=True, help="Giờ sinh HH:MM (ví dụ: 08:30) - CẦN CHÍNH XÁC")
    parser.add_argument("--timezone", default="+07:00", help="Múi giờ: +07:00 (VN), +08:00, etc. Mặc định +07:00")
    parser.add_argument("--name", default="", help="Tên người (tùy chọn)")
    parser.add_argument("--output", default="", help="File lưu kết quả (tùy chọn)")
    parser.add_argument("--json", action="store_true", help="Xuất JSON thay vì text")
    
    args = parser.parse_args()
    
    try:
        dt_utc, dt_local, tz = parse_datetime(args.date, args.time, args.timezone)
    except Exception as e:
        print(f"Lỗi parse ngày giờ: {e}")
        print("Ví dụ đúng: --date 1990-05-15 --time 08:30 --timezone +07:00")
        sys.exit(1)
    
    print(f"\n🔮 Đang tính toán Human Design cho {args.name or 'bạn'}...")
    print(f"📅 Ngày sinh local: {dt_local} {tz}")
    print(f"🌐 Ngày sinh UTC: {dt_utc} (dùng để tính toán thiên văn)")
    print(f"⏳ Đang tính toán với Swiss Ephemeris (độ chính xác <1 arc second)...\n")
    
    chart = calculate_hd_chart(dt_utc)
    
    # Tạo báo cáo
    text_report = format_chart_text(chart)
    deep_report = analyze_chart(chart)
    
    full_report = f"""
{'='*80}
HUMAN DESIGN ANALYSIS - {args.name or 'CHART'}
{'='*80}
Ngày sinh (local): {dt_local} {tz}
Ngày sinh (UTC): {dt_utc}
Ngày Design (vô thức): {chart['design_datetime']} UTC

{text_report}

{'='*80}
PHÂN TÍCH CHUYÊN SÂU
{'='*80}

{deep_report}
"""
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(full_report)
        print(f"✅ Đã lưu kết quả vào {args.output}")
    else:
        print(full_report)
    
    if args.json:
        import json
        # Chuẩn bị JSON serializable
        json_data = {
            "name": args.name,
            "birth_local": str(dt_local),
            "birth_utc": str(dt_utc),
            "timezone": tz,
            "type": chart['type'],
            "strategy": chart['strategy'],
            "authority": chart['authority'],
            "profile": chart['profile'],
            "definition": chart['definition'],
            "incarnation_cross": chart['incarnation_cross'],
            "cross_type": chart['cross_type'],
            "defined_centers": chart['defined_centers'],
            "defined_channels": chart['defined_channels'],
            "all_activated_gates": chart['all_activated_gates'],
            "personality_gates": {k: {"gate": v["gate"], "line": v["line"], "longitude": v["longitude"]} for k,v in chart['personality_gates'].items()},
            "design_gates": {k: {"gate": v["gate"], "line": v["line"], "longitude": v["longitude"]} for k,v in chart['design_gates'].items()},
        }
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        if args.output:
            json_file = args.output.replace(".txt", ".json") if ".txt" in args.output else args.output + ".json"
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            print(f"✅ Đã lưu JSON vào {json_file}")
        else:
            print("\n--- JSON ---\n")
            print(json_str)

if __name__ == "__main__":
    main()

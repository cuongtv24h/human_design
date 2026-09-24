"""
Ví dụ Client gọi Human Design MCP Server
Mô phỏng cách LLM core gọi tools qua MCP
"""

import asyncio
import json
from datetime import datetime

# Mô phỏng gọi tool trực tiếp (không qua MCP transport, để test logic)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
sys.path.insert(0, os.path.dirname(__file__))

from server import (
    calculate_human_design_chart,
    analyze_human_design_deep,
    get_gate_info,
    get_center_info,
    get_channel_info,
    get_profile_info,
    compare_charts,
    generate_full_report
)

def test_full_flow():
    print("="*80)
    print("TEST 1: Tính toán chart cơ bản")
    print("="*80)
    chart = calculate_human_design_chart(
        birth_date="1990-05-15",
        birth_time="08:30",
        timezone="+07:00",
        name="Nguyen Van A",
        birth_location="Hanoi, Vietnam"
    )
    print(json.dumps(chart, ensure_ascii=False, indent=2)[:2000] + "\n... (rút gọn)")
    print(f"\nType: {chart['type']}, Authority: {chart['authority']}, Profile: {chart['profile']}")
    
    print("\n" + "="*80)
    print("TEST 2: Phân tích chuyên sâu")
    print("="*80)
    analysis = analyze_human_design_deep(
        birth_date="1990-05-15",
        birth_time="08:30",
        timezone="+07:00",
        name="Nguyen Van A",
        focus_area="full"
    )
    print(analysis[:3000] + "\n... (rút gọn)")
    
    print("\n" + "="*80)
    print("TEST 3: Tra cứu Gate 10")
    print("="*80)
    gate = get_gate_info(gate_number=10)
    print(json.dumps(gate, ensure_ascii=False, indent=2))
    
    print("\n" + "="*80)
    print("TEST 4: Tra cứu Center G")
    print("="*80)
    center = get_center_info(center_name="G")
    print(json.dumps(center, ensure_ascii=False, indent=2)[:1500])
    
    print("\n" + "="*80)
    print("TEST 5: Tra cứu Channel 10-20")
    print("="*80)
    channel = get_channel_info(gate1=10, gate2=20)
    print(json.dumps(channel, ensure_ascii=False, indent=2))
    
    print("\n" + "="*80)
    print("TEST 6: Tra cứu Profile 2/4")
    print("="*80)
    profile = get_profile_info(profile="2/4")
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    
    print("\n" + "="*80)
    print("TEST 7: So sánh 2 người (Composite)")
    print("="*80)
    comp = compare_charts(
        person1_date="1990-05-15",
        person1_time="08:30",
        person1_name="Nguyen Van A",
        person2_date="1992-08-20",
        person2_time="14:00",
        person2_name="Tran Thi B",
        timezone="+07:00"
    )
    print(json.dumps(comp, ensure_ascii=False, indent=2))
    
    print("\n" + "="*80)
    print("TEST 8: Tạo báo cáo đầy đủ")
    print("="*80)
    report = generate_full_report(
        birth_date="1990-05-15",
        birth_time="08:30",
        timezone="+07:00",
        name="Nguyen Van A",
        birth_location="Hanoi, Vietnam",
        format="markdown"
    )
    print(report[:4000] + "\n... (rút gọn)")
    
    print("\n✅ Tất cả test hoàn thành!")

if __name__ == "__main__":
    test_full_flow()

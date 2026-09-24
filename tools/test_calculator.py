from datetime import datetime
from hd_calculator import calculate_hd_chart, format_chart_text
from hd_analyzer import analyze_chart

# Test với một số ngày sinh nổi tiếng để kiểm tra
test_cases = [
    datetime(1987, 1, 1, 12, 0, 0),  # Gần Rave New Year
    datetime(1990, 6, 15, 8, 30, 0),
    datetime(2000, 1, 1, 0, 0, 0),
    datetime(1995, 12, 25, 15, 45, 0),
]

for dt in test_cases:
    print("\n" + "="*80)
    chart = calculate_hd_chart(dt)
    print(format_chart_text(chart))
    print("\n--- Phân tích ngắn ---")
    print(f"Type: {chart['type']}, Authority: {chart['authority']}, Profile: {chart['profile']}, Definition: {chart['definition']}")
    print(f"Cross: {chart['incarnation_cross']}")

print("\n\nTest hoàn thành!")

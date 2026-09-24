"""
Test tool Manifestor với tất cả Profiles
"""

from hd_advanced_tools import analyze_manifestor_deep, analyze_fear_gates, analyze_love_gates
from hd_calculator import calculate_hd_chart
from datetime import datetime

# Test với Manifestor các Profile khác nhau
test_cases = [
    (datetime(1980, 9, 10, 12, 0), "Manifestor 1/4"),
    (datetime(1981, 6, 15, 12, 0), "Manifestor 2/4"),
    (datetime(1981, 7, 1, 12, 0), "Manifestor 1/3"),
    (datetime(1981, 10, 5, 12, 0), "Manifestor 3/5"),
    (datetime(1984, 3, 5, 12, 0), "Manifestor 4/1"),
    (datetime(1985, 3, 5, 12, 0), "Manifestor 4/6"),
    (datetime(1998, 3, 10, 12, 0), "Manifestor 3/6"),
]

print("=== TEST MANIFESTOR TOOL VỚI TẤT CẢ PROFILES ===\n")

for dt, label in test_cases:
    chart = calculate_hd_chart(dt)
    result = analyze_manifestor_deep(dt)
    
    print(f"{label}:")
    print(f"  Type: {chart['type']} (is_manifestor: {result['is_manifestor']})")
    print(f"  Profile: {chart['profile']}")
    print(f"  Authority: {chart['authority']}")
    print(f"  Technical check - Throat: {result['technical_check']['has_throat_defined']}, Sacral: {result['technical_check']['has_sacral_defined']}, Motor to Throat: {len(result['technical_check']['motor_to_throat'])} channels")
    
    if result['is_manifestor']:
        print(f"  Deep dive có: {list(result.get('deep_dive', {}).keys())}")
    print()

# Test với non-Manifestor
print("\n=== TEST VỚI NON-MANIFESTOR (Generator) ===\n")
dt_gen = datetime(1990, 5, 15, 1, 30)
chart_gen = calculate_hd_chart(dt_gen)
result_gen = analyze_manifestor_deep(dt_gen)
print(f"Type: {chart_gen['type']}, Profile: {chart_gen['profile']}")
print(f"Is Manifestor: {result_gen['is_manifestor']}")
print(f"Note: {result_gen.get('note', 'No note')}")

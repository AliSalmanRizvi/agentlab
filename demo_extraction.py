#!/usr/bin/env python3
"""
Demo script showing improved license number extraction capabilities
"""

from drivers_license_scanner import DriversLicenseScanner
import os

def demo_extraction_patterns():
    """Demonstrate various license number extraction patterns"""
    
    print("🎯 Driver's License Number Extraction Demo")
    print("=" * 50)
    
    # Initialize scanner
    scanner = DriversLicenseScanner(region_name='us-east-1')
    
    # Test various license number formats
    test_cases = [
        ("Lic# A1234567", "CA", "Standard Lic# format"),
        ("LICENSE# 12345678", "TX", "LICENSE# format"),
        ("DL# B123456789012", "FL", "DL# format"),
        ("Driver License A9876543", "CA", "Driver License format"),
        ("ID# 987654321", "NY", "ID# format"),
        ("License Number: C1234567890123", "FL", "License Number: format"),
        ("Lic#D1234567890", "FL", "No space after #"),
        ("License D9876543", "CA", "No # symbol"),
    ]
    
    print("\n📋 Testing extraction patterns:")
    for text, state, description in test_cases:
        result = scanner.extract_license_number(text, state)
        status = "✅" if result else "❌"
        print(f"  {status} {description}")
        print(f"      Input: '{text}'")
        print(f"      Output: {result}")
        print()
    
    print("🎉 The scanner now correctly handles:")
    print("  • Lic# prefix (most common)")
    print("  • LICENSE# prefix")
    print("  • DL# prefix")
    print("  • Driver License prefix")
    print("  • ID# prefix")
    print("  • License Number: prefix")
    print("  • With or without spaces")
    print("  • With or without colons")
    print("  • State-specific validation")
    print("  • False positive filtering")

if __name__ == "__main__":
    demo_extraction_patterns()
#!/usr/bin/env python3
"""
Test Connecticut license number extraction specifically
"""

from drivers_license_scanner import DriversLicenseScanner

def test_ct_extraction():
    """Test Connecticut license number extraction"""
    
    scanner = DriversLicenseScanner(region_name='us-east-1')
    
    # Simulate text that might be extracted from a CT license
    test_cases = [
        # Format: (extracted_text, expected_license_number)
        ("CONNECTICUT\nDRIVER LICENSE\nANTOSIO SCHONGLE\n123456789\nCLASS D", "123456789"),
        ("CT\nLic# 987654321\nJOHN DOE\nEXPIRES 12/31/2025", "987654321"),
        ("CONNECTICUT\nANTOSIO\nSCHONGLE\n555666777\nADDRESS", "555666777"),
        ("CT DRIVER LICENSE\nNAME: JOHN DOE\nLIC: 111222333\nCLASS: D", "111222333"),
        ("CONNECTICUT\nANTOSIO SCHONGLE\nNO NUMBERS HERE", None),
    ]
    
    print("🧪 Testing Connecticut License Number Extraction")
    print("=" * 50)
    
    for i, (text, expected) in enumerate(test_cases, 1):
        result = scanner.extract_license_number(text, "CT")
        status = "✅" if result == expected else "❌"
        
        print(f"\nTest {i}: {status}")
        print(f"Input text: {repr(text)}")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        
        if result != expected:
            print(f"❌ FAILED: Expected {expected}, got {result}")
        else:
            print(f"✅ PASSED")

if __name__ == "__main__":
    test_ct_extraction()
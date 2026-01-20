#!/usr/bin/env python3
"""
Test script for the Driver's License Scanner Agent

This script tests the scanner functionality without requiring actual AWS credentials
by mocking the Textract service for demonstration purposes.
"""

import json
import base64
import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from license_scanner.scanner import DriversLicenseScanner, LicenseInfo

def create_mock_textract_response():
    """Create a mock AWS Textract response for testing"""
    return {
        'Blocks': [
            {
                'BlockType': 'LINE',
                'Text': 'CALIFORNIA'
            },
            {
                'BlockType': 'LINE', 
                'Text': 'DRIVER LICENSE'
            },
            {
                'BlockType': 'LINE',
                'Text': 'Lic# A1234567'
            },
            {
                'BlockType': 'LINE',
                'Text': 'CLASS C'
            },
            {
                'BlockType': 'LINE',
                'Text': 'EXPIRES 01/15/2025'
            },
            {
                'BlockType': 'LINE',
                'Text': 'DOB 03/15/1990'
            }
        ]
    }

def test_state_identification():
    """Test state identification functionality"""
    print("🧪 Testing state identification...")
    
    scanner = DriversLicenseScanner(region_name='us-east-1')
    
    test_cases = [
        ("CALIFORNIA DRIVER LICENSE", "CA"),
        ("STATE OF TEXAS", "TX"),
        ("FLORIDA DL", "FL"),
        ("NEW YORK DRIVER LICENSE", "NY"),
        ("INVALID STATE", None)
    ]
    
    for text, expected_state in test_cases:
        result = scanner.identify_state(text)
        status = "✅" if result == expected_state else "❌"
        print(f"  {status} '{text}' -> {result} (expected: {expected_state})")

def test_license_number_extraction():
    """Test license number extraction functionality"""
    print("\n🧪 Testing license number extraction...")
    
    scanner = DriversLicenseScanner(region_name='us-east-1')
    
    test_cases = [
        ("Lic# A1234567 CLASS C", "CA", "A1234567"),
        ("LICENSE# 12345678", "TX", "12345678"),
        ("DL# B123456789012", "FL", "B123456789012"),
        ("Driver License A9876543", "CA", "A9876543"),
        ("ID# 987654321", "NY", "987654321"),
        ("License Number: C5555555555555", "FL", "C5555555555555"),
        ("NO VALID LICENSE HERE", None, None),
        ("EXPIRES 12/31/2025 CLASS A", None, None),  # Should not extract date
        ("Lic#D1234567890123", "FL", "D1234567890123"),  # No space after #
        ("License D9876543", "CA", "D9876543")  # No # symbol
    ]
    
    for text, state, expected_license in test_cases:
        result = scanner.extract_license_number(text, state)
        status = "✅" if result == expected_license else "❌"
        print(f"  {status} '{text}' ({state}) -> {result} (expected: {expected_license})")

def test_confidence_calculation():
    """Test confidence score calculation"""
    print("\n🧪 Testing confidence calculation...")
    
    scanner = DriversLicenseScanner(region_name='us-east-1')
    
    test_cases = [
        (LicenseInfo(license_number="A1234567", state="CA"), "High confidence"),
        (LicenseInfo(license_number="A1234567", state=None), "Medium confidence"),
        (LicenseInfo(license_number=None, state="CA"), "Low confidence"),
        (LicenseInfo(license_number=None, state=None), "No confidence")
    ]
    
    for license_info, description in test_cases:
        score = scanner.calculate_confidence(license_info)
        print(f"  📊 {description}: {score:.2%}")

@patch('boto3.client')
def test_full_scan_mock(mock_boto_client):
    """Test full scanning process with mocked AWS Textract"""
    print("\n🧪 Testing full scan with mock data...")
    
    # Mock the Textract client
    mock_textract = Mock()
    mock_textract.detect_document_text.return_value = create_mock_textract_response()
    mock_boto_client.return_value = mock_textract
    
    # Create scanner and test (with region specified)
    scanner = DriversLicenseScanner(region_name='us-east-1')
    
    # Create fake base64 image data
    fake_image_data = base64.b64encode(b"fake_image_bytes").decode('utf-8')
    
    # Scan the "license"
    result = scanner.scan_license(fake_image_data)
    
    print(f"  📄 Scan Result:")
    print(f"    Success: {result['success']}")
    print(f"    License Number: {result['license_number']}")
    print(f"    State: {result['state']}")
    print(f"    Confidence: {result['confidence_score']:.2%}")
    
    # Verify results
    if result['success'] and result['state'] == 'CA' and result['license_number'] == 'A1234567':
        print("  ✅ Mock scan test passed!")
    else:
        print("  ❌ Mock scan test failed!")

def test_supported_states():
    """Test supported states functionality"""
    print("\n🧪 Testing supported states...")
    
    scanner = DriversLicenseScanner(region_name='us-east-1')
    states = scanner.US_STATES
    
    print(f"  📍 Total supported states: {len(states)}")
    print(f"  🗺️ Sample states: {sorted(list(states))[:10]}...")
    
    # Verify we have all 50 states + DC
    if len(states) >= 51:
        print("  ✅ All US states supported!")
    else:
        print("  ❌ Missing some US states!")

def test_license_patterns():
    """Test license number patterns"""
    print("\n🧪 Testing license patterns...")
    
    scanner = DriversLicenseScanner(region_name='us-east-1')
    patterns = scanner.LICENSE_PATTERNS
    
    print(f"  🔍 Available patterns: {len(patterns)}")
    for state, pattern in list(patterns.items())[:5]:
        print(f"    {state}: {pattern}")
    
    if 'CA' in patterns and 'TX' in patterns:
        print("  ✅ Key state patterns available!")
    else:
        print("  ❌ Missing key state patterns!")

def main():
    """Run all tests"""
    print("🚀 Driver's License Scanner Agent - Test Suite")
    print("=" * 50)
    
    try:
        test_state_identification()
        test_license_number_extraction()
        test_confidence_calculation()
        test_full_scan_mock()
        test_supported_states()
        test_license_patterns()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("\n📋 Next steps:")
        print("  1. Configure AWS credentials: aws configure")
        print("  2. Test with real image: python license_scanner_api.py image.jpg")
        print("  3. Start web service: python web_service.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Please check your installation and try again.")

if __name__ == "__main__":
    main()
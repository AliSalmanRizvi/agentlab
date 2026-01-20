#!/usr/bin/env python3
"""
Run all tests for the Driver's License Scanner
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_main_tests():
    """Run the main test suite"""
    print("🧪 Running main test suite...")
    os.system(f"python3 {os.path.join('tests', 'test_scanner.py')}")

def run_ct_tests():
    """Run Connecticut-specific tests"""
    print("\n🧪 Running Connecticut-specific tests...")
    os.system(f"python3 {os.path.join('tests', 'test_ct_extraction.py')}")

def main():
    """Run all tests"""
    print("🚀 US Driver's License Scanner - Test Suite")
    print("=" * 50)
    
    # Set AWS region for tests
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    run_main_tests()
    run_ct_tests()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()
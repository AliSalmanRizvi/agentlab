#!/usr/bin/env python3
"""
Command Line Interface for the Driver's License Scanner
"""

import sys
import os
import argparse
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from license_scanner import LicenseScannerAPI

def main():
    """Command line interface for testing the scanner"""
    parser = argparse.ArgumentParser(description='US Driver\'s License Scanner')
    parser.add_argument('image_path', help='Path to driver\'s license image')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    
    args = parser.parse_args()
    
    # Initialize API
    api = LicenseScannerAPI(region_name=args.region)
    
    # Scan the license
    result = api.scan_from_file(args.image_path)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result['success']:
            print(f"✅ Scan successful!")
            print(f"License Number: {result['license_number'] or 'Not found'}")
            print(f"State: {result['state'] or 'Not found'}")
            print(f"Confidence: {result['confidence_score']:.2%}")
        else:
            print(f"❌ Scan failed: {result['error']}")

if __name__ == "__main__":
    main()
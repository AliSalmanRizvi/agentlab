#!/usr/bin/env python3
"""
Driver's License Scanner API

A user-friendly API wrapper for the driver's license scanner agent.
Supports multiple input formats and provides enhanced error handling.
"""

import json
import base64
import io
from pathlib import Path
from PIL import Image
from drivers_license_scanner import DriversLicenseScanner
import logging

logger = logging.getLogger(__name__)

class LicenseScannerAPI:
    """API wrapper for the driver's license scanner"""
    
    def __init__(self, region_name='us-east-1'):
        """Initialize the API with the scanner"""
        self.scanner = DriversLicenseScanner(region_name=region_name)
    
    def _image_to_base64(self, image_path: str) -> str:
        """
        Convert image file to base64 string
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
                return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error reading image file: {e}")
    
    def _validate_image(self, image_data: bytes) -> bool:
        """
        Validate that the image data is a valid image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            return True
        except Exception:
            return False
    
    def scan_from_file(self, image_path: str) -> dict:
        """
        Scan driver's license from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with scan results
        """
        try:
            if not Path(image_path).exists():
                return {
                    'success': False,
                    'error': f'Image file not found: {image_path}'
                }
            
            # Convert to base64
            image_base64 = self._image_to_base64(image_path)
            
            # Validate image
            image_bytes = base64.b64decode(image_base64)
            if not self._validate_image(image_bytes):
                return {
                    'success': False,
                    'error': 'Invalid image format'
                }
            
            # Scan the license
            return self.scanner.scan_license(image_base64)
            
        except Exception as e:
            logger.error(f"Error scanning from file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def scan_from_base64(self, image_base64: str) -> dict:
        """
        Scan driver's license from base64 encoded image
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Dictionary with scan results
        """
        try:
            # Validate base64 and image
            image_bytes = base64.b64decode(image_base64)
            if not self._validate_image(image_bytes):
                return {
                    'success': False,
                    'error': 'Invalid image format'
                }
            
            # Scan the license
            return self.scanner.scan_license(image_base64)
            
        except Exception as e:
            logger.error(f"Error scanning from base64: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def scan_from_bytes(self, image_bytes: bytes) -> dict:
        """
        Scan driver's license from raw image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with scan results
        """
        try:
            # Validate image
            if not self._validate_image(image_bytes):
                return {
                    'success': False,
                    'error': 'Invalid image format'
                }
            
            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Scan the license
            return self.scanner.scan_license(image_base64)
            
        except Exception as e:
            logger.error(f"Error scanning from bytes: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supported_states(self) -> list:
        """
        Get list of supported US states
        
        Returns:
            List of state abbreviations
        """
        return sorted(list(self.scanner.US_STATES))
    
    def get_state_pattern(self, state: str) -> str:
        """
        Get license number pattern for a specific state
        
        Args:
            state: State abbreviation
            
        Returns:
            Regex pattern for the state's license numbers
        """
        return self.scanner.LICENSE_PATTERNS.get(state.upper(), 'Pattern not available')

# CLI interface for testing
def main():
    """Command line interface for testing the scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Driver\'s License Scanner')
    parser.add_argument('image_path', help='Path to driver\'s license image')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Initialize API
    api = LicenseScannerAPI()
    
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
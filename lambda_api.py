#!/usr/bin/env python3
"""
Lambda-specific Driver's License Scanner API

A simplified API wrapper for Lambda that doesn't use PIL for image validation.
AWS Textract handles image validation directly.
"""

import json
import base64
import sys
import os
from pathlib import Path
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from license_scanner.scanner import DriversLicenseScanner

logger = logging.getLogger(__name__)

class LicenseScannerAPI:
    """Lambda-compatible API wrapper for the driver's license scanner"""
    
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
    
    def _validate_base64(self, image_base64: str) -> bool:
        """
        Basic validation of base64 string
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            True if valid base64, False otherwise
        """
        try:
            # Try to decode base64
            image_bytes = base64.b64decode(image_base64)
            
            # Basic size check (should be at least 100 bytes for a valid image)
            if len(image_bytes) < 100:
                return False
            
            # Check for common image file signatures
            # JPEG: FF D8 FF
            # PNG: 89 50 4E 47
            # GIF: 47 49 46 38
            # BMP: 42 4D
            image_signatures = [
                b'\xFF\xD8\xFF',  # JPEG
                b'\x89\x50\x4E\x47',  # PNG
                b'\x47\x49\x46\x38',  # GIF
                b'\x42\x4D',  # BMP
            ]
            
            return any(image_bytes.startswith(sig) for sig in image_signatures)
            
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
            
            # Basic validation
            if not self._validate_base64(image_base64):
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
            # Basic validation
            if not self._validate_base64(image_base64):
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
            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Basic validation
            if not self._validate_base64(image_base64):
                return {
                    'success': False,
                    'error': 'Invalid image format'
                }
            
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
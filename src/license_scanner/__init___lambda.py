"""
US Driver's License Scanner - Lambda Version

A complete AI-powered agent system that scans US driver's licenses 
to extract license numbers and state information using AWS Textract OCR technology.

Lambda version without PIL dependencies.
"""

from .scanner import DriversLicenseScanner, LicenseInfo

__version__ = "1.0.0"
__author__ = "AI Agent Developer"
__description__ = "US Driver's License Scanner using AWS Textract - Lambda Version"

__all__ = [
    "DriversLicenseScanner",
    "LicenseInfo"
]
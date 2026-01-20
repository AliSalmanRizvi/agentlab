"""
US Driver's License Scanner

A complete AI-powered agent system that scans US driver's licenses 
to extract license numbers and state information using AWS Textract OCR technology.
"""

from .scanner import DriversLicenseScanner, LicenseInfo
from .api import LicenseScannerAPI

__version__ = "1.0.0"
__author__ = "AI Agent Developer"
__description__ = "US Driver's License Scanner using AWS Textract"

__all__ = [
    "DriversLicenseScanner",
    "LicenseInfo", 
    "LicenseScannerAPI"
]
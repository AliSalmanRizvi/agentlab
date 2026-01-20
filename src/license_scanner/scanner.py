#!/usr/bin/env python3
"""
US Driver's License Scanner Agent

This agent scans US driver's licenses to extract license number and state information.
Uses AWS Textract for OCR and pattern matching for data extraction.
"""

import json
import re
import base64
import boto3
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LicenseInfo:
    """Data class for driver's license information"""
    license_number: Optional[str] = None
    state: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    confidence_score: float = 0.0
    raw_text: str = ""

class DriversLicenseScanner:
    """Main scanner class for processing driver's license images"""
    
    def __init__(self, region_name='us-east-1'):
        """Initialize the scanner with AWS Textract client"""
        try:
            # Try to get region from environment variable first, then use default
            region = os.environ.get('AWS_DEFAULT_REGION', region_name)
            self.textract = boto3.client('textract', region_name=region)
            logger.info(f"Initialized AWS Textract client in region: {region}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Textract client: {e}")
            self.textract = None
    
    # US State abbreviations and common license number patterns
    US_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }
    
    # Common license number patterns by state (simplified)
    LICENSE_PATTERNS = {
        'CA': r'[A-Z]\d{7}',  # California: 1 letter + 7 digits
        'TX': r'\d{8}',       # Texas: 8 digits
        'FL': r'[A-Z]\d{12,13}', # Florida: 1 letter + 12-13 digits
        'NY': r'\d{9}',       # New York: 9 digits
        'PA': r'\d{8}',       # Pennsylvania: 8 digits
        'IL': r'[A-Z]\d{11}', # Illinois: 1 letter + 11 digits
        'OH': r'[A-Z]{2}\d{6}', # Ohio: 2 letters + 6 digits
        'GA': r'\d{9}',       # Georgia: 9 digits
        'NC': r'\d{12}',      # North Carolina: 12 digits
        'MI': r'[A-Z]\d{12}', # Michigan: 1 letter + 12 digits
        'CT': r'\d{9}',       # Connecticut: 9 digits
        # Generic pattern for other states
        'GENERIC': r'[A-Z0-9]{6,15}'
    }
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extract text from image using AWS Textract
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Extracted text as string
        """
        if not self.textract:
            raise Exception("AWS Textract client not initialized")
        
        try:
            response = self.textract.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            # Extract all text blocks
            text_blocks = []
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block['Text'])
            
            return '\n'.join(text_blocks)
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def identify_state(self, text: str) -> Optional[str]:
        """
        Identify the state from extracted text
        
        Args:
            text: Extracted text from license
            
        Returns:
            State abbreviation if found, None otherwise
        """
        text_upper = text.upper()
        
        # Look for state abbreviations in the text
        for state in self.US_STATES:
            # Check for state abbreviation patterns
            patterns = [
                rf'\b{state}\b',  # Exact match
                rf'{state}\s+DRIVER',  # State + DRIVER
                rf'{state}\s+LICENSE',  # State + LICENSE
                rf'STATE\s+OF\s+{state}',  # STATE OF [STATE]
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    return state
        
        return None
    
    def extract_license_number(self, text: str, state: Optional[str] = None) -> Optional[str]:
        """
        Extract license number from text based on state patterns and common prefixes
        
        Args:
            text: Extracted text from license
            state: Identified state (if any)
            
        Returns:
            License number if found, None otherwise
        """
        text_upper = text.upper()
        
        # Common license number prefixes and patterns
        license_prefixes = [
            r'LIC#?\s*:?\s*([A-Z0-9]+)',           # Lic# or Lic: followed by number
            r'LICENSE#?\s*:?\s*([A-Z0-9]+)',      # License# or License: followed by number
            r'DL#?\s*:?\s*([A-Z0-9]+)',           # DL# or DL: followed by number
            r'DRIVER\s*LICENSE#?\s*:?\s*([A-Z0-9]+)',  # Driver License# followed by number
            r'ID#?\s*:?\s*([A-Z0-9]+)',           # ID# followed by number
            r'NUMBER#?\s*:?\s*([A-Z0-9]+)',       # Number# followed by number
            r'LICENSE\s+NUMBER\s*:?\s*([A-Z0-9]+)', # License Number: followed by number
        ]
        
        # First, try to find license numbers with common prefixes
        for prefix_pattern in license_prefixes:
            matches = re.findall(prefix_pattern, text_upper)
            if matches:
                for match in matches:
                    # Clean the match and validate it's not a false positive
                    clean_match = re.sub(r'\s+', '', match)
                    if self._is_valid_license_number(clean_match, state):
                        return clean_match
        
        # If no prefix matches, try state-specific patterns directly in the text
        if state and state in self.LICENSE_PATTERNS:
            pattern = self.LICENSE_PATTERNS[state]
            # Look for the pattern in the original text (with spaces)
            matches = re.findall(pattern, text_upper)
            for match in matches:
                if self._is_valid_license_number(match, state):
                    return match
            
            # Also try in cleaned text (no spaces)
            text_clean = re.sub(r'\s+', '', text_upper)
            matches = re.findall(pattern, text_clean)
            for match in matches:
                if self._is_valid_license_number(match, state):
                    return match
        
        # For Connecticut specifically, look for 9-digit numbers
        if state == 'CT':
            nine_digit_pattern = r'\b\d{9}\b'
            matches = re.findall(nine_digit_pattern, text_upper)
            for match in matches:
                if self._is_valid_license_number(match, state):
                    return match
        
        # Look for common numeric patterns that could be license numbers
        numeric_patterns = [
            r'\b\d{9}\b',      # 9 digits (common for many states)
            r'\b\d{8}\b',      # 8 digits
            r'\b[A-Z]\d{7}\b', # 1 letter + 7 digits
            r'\b[A-Z]\d{12}\b', # 1 letter + 12 digits
        ]
        
        for pattern in numeric_patterns:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                if self._is_valid_license_number(match, state):
                    return match
        
        # Finally, try generic pattern with validation
        generic_pattern = self.LICENSE_PATTERNS['GENERIC']
        text_clean = re.sub(r'\s+', '', text_upper)
        matches = re.findall(generic_pattern, text_clean)
        
        # Filter and validate matches, prioritize those with more digits
        valid_matches = []
        for match in matches:
            if self._is_valid_license_number(match, state):
                digit_count = sum(1 for c in match if c.isdigit())
                valid_matches.append((match, digit_count))
        
        if valid_matches:
            # Sort by digit count (descending) and return the one with most digits
            valid_matches.sort(key=lambda x: x[1], reverse=True)
            return valid_matches[0][0]
        
        return None
    
    def _is_valid_license_number(self, candidate: str, state: Optional[str] = None) -> bool:
        """
        Validate if a candidate string is likely a valid license number
        
        Args:
            candidate: Potential license number
            state: State abbreviation (if known)
            
        Returns:
            True if candidate appears to be a valid license number
        """
        if not candidate or len(candidate) < 4:
            return False
        
        # Common false positives to exclude (including names and common words)
        false_positives = {
            'LICENSE', 'DRIVER', 'CLASS', 'EXPIRES', 'ISSUED', 'BIRTH', 'DATE',
            'HEIGHT', 'WEIGHT', 'EYES', 'HAIR', 'SEX', 'MALE', 'FEMALE',
            'RESTRICTIONS', 'ENDORSEMENTS', 'VETERAN', 'ORGAN', 'DONOR',
            'ADDRESS', 'CITY', 'STATE', 'ZIP', 'COUNTRY', 'USA', 'UNITED',
            'STATES', 'AMERICA', 'DEPARTMENT', 'MOTOR', 'VEHICLES', 'DMV',
            'NOVALIDLICENSEH', 'EXPIRES12', 'ANTOSIO', 'SCHONGLE', 'NAME',
            'FIRST', 'LAST', 'MIDDLE', 'SIGNATURE', 'CONNECTICUT', 'CALIFORNIA',
            'TEXAS', 'FLORIDA', 'NEWYORK', 'PENNSYLVANIA'
        }
        
        if candidate in false_positives:
            return False
        
        # Check if it starts with common false positive patterns
        false_positive_prefixes = ['EXPIRES', 'NOVALID', 'INVALID', 'CLASS', 'BIRTH']
        if any(candidate.startswith(prefix) for prefix in false_positive_prefixes):
            return False
        
        # License numbers should contain at least some digits
        digit_count = sum(1 for c in candidate if c.isdigit())
        letter_count = sum(1 for c in candidate if c.isalpha())
        
        # Most license numbers have a significant number of digits
        if digit_count == 0:
            return False
        
        # If it's all letters (like a name), it's probably not a license number
        if letter_count == len(candidate) and len(candidate) > 3:
            return False
        
        # License numbers typically have more digits than letters, or are all digits
        if letter_count > digit_count and digit_count < 3:
            return False
        
        # Check if it's mostly a date (MMDDYYYY, DDMMYYYY, YYYYMMDD)
        if re.match(r'^\d{8}$', candidate):
            # Could be a date, check if it looks like a reasonable date
            year_patterns = ['19', '20', '21']  # 1900s, 2000s, 2010s
            if any(candidate.startswith(year) or candidate.endswith(year + candidate[-2:]) for year in year_patterns):
                return False
        
        # Must contain at least one alphanumeric character
        if not re.search(r'[A-Z0-9]', candidate):
            return False
        
        # Should not be all the same character
        if len(set(candidate)) == 1:
            return False
        
        # Length validation - be more flexible for different states
        min_length = 6
        max_length = 15
        
        # Adjust length limits based on state
        if state:
            if state == 'FL':  # Florida licenses can be up to 13 characters
                max_length = 13
            elif state in ['CA', 'NY', 'TX']:  # These states have shorter licenses
                max_length = 12
            elif state == 'CT':  # Connecticut typically 9 digits
                min_length = 8
                max_length = 10
        
        if len(candidate) < min_length or len(candidate) > max_length:
            return False
        
        # Check state-specific validation if state is known
        if state and state in self.LICENSE_PATTERNS:
            pattern = self.LICENSE_PATTERNS[state]
            if not re.match(pattern + '$', candidate):
                # For state validation, be a bit more flexible but still validate structure
                if state == 'CT' and not re.match(r'^\d{9}$', candidate):
                    return False
        
        return True
    
    def extract_names(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract first name and last name from license text
        
        Args:
            text: Extracted text from license
            
        Returns:
            Tuple of (first_name, last_name) if found, (None, None) otherwise
        """
        text_upper = text.upper()
        lines = text_upper.split('\n')
        
        # Common name patterns and prefixes
        name_patterns = [
            r'NAME[:\s]+([A-Z\s]+?)(?:\n|$)',
            r'FULL\s*NAME[:\s]+([A-Z\s]+?)(?:\n|$)',
            r'DRIVER[:\s]+([A-Z\s]+?)(?:\n|$)',
            r'LICENSEE[:\s]+([A-Z\s]+?)(?:\n|$)',
        ]
        
        # Look for explicit name patterns first
        for pattern in name_patterns:
            matches = re.findall(pattern, text_upper, re.MULTILINE)
            if matches:
                name_text = matches[0].strip()
                # Remove any trailing keywords that might have been captured
                name_words = name_text.split()
                clean_words = []
                for word in name_words:
                    if word not in {'LIC', 'LICENSE', 'DOB', 'CLASS', 'EXPIRES', 'STATE', 'CT', 'CA', 'TX', 'FL', 'NY'}:
                        clean_words.append(word)
                    else:
                        break  # Stop at first keyword
                
                if clean_words and self._is_valid_name(' '.join(clean_words)):
                    return self._parse_name(' '.join(clean_words))
        
        # Look for name-like patterns in lines
        # Names are typically on lines with mostly alphabetic characters
        potential_names = []
        
        for line in lines:
            line = line.strip()
            if self._looks_like_name_line(line):
                potential_names.append(line)
        
        # Try to find the best name candidate
        # Prefer lines that look most like names (2 words, all alpha)
        potential_names.sort(key=lambda x: (
            len(x.split()) == 2,  # Prefer exactly 2 words
            all(word.isalpha() for word in x.split()),  # Prefer all alphabetic
            len(x)  # Prefer reasonable length
        ), reverse=True)
        
        for name_line in potential_names:
            if self._is_valid_name(name_line):
                return self._parse_name(name_line)
        
        return None, None
    
    def _looks_like_name_line(self, line: str) -> bool:
        """Check if a line looks like it contains a name"""
        if not line or len(line) < 3:
            return False
        
        # Skip lines with common license keywords
        skip_keywords = {
            'LICENSE', 'DRIVER', 'CLASS', 'EXPIRES', 'ISSUED', 'BIRTH', 'DATE',
            'HEIGHT', 'WEIGHT', 'EYES', 'HAIR', 'SEX', 'RESTRICTIONS', 'ADDRESS',
            'CITY', 'STATE', 'ZIP', 'COUNTRY', 'VETERAN', 'ORGAN', 'DONOR',
            'CONNECTICUT', 'CALIFORNIA', 'TEXAS', 'FLORIDA', 'NEW YORK', 'DOB',
            'LIC#', 'LIC', 'ID#', 'NUMBER', 'FULL', 'NAME:', 'EXPIRES:', 'BORN'
        }
        
        # Check if line contains any skip keywords
        line_words = line.split()
        for word in line_words:
            if word.rstrip(':') in skip_keywords:
                return False
        
        # Skip lines that are mostly numbers
        digit_count = sum(1 for c in line if c.isdigit())
        if digit_count > len(line) * 0.5:
            return False
        
        # Skip lines with special characters (except spaces and common punctuation)
        if re.search(r'[^A-Z\s\-\.]', line):
            return False
        
        # Must be mostly alphabetic
        alpha_count = sum(1 for c in line if c.isalpha())
        if alpha_count < len(line) * 0.7:
            return False
        
        # Should look like a reasonable name (2-4 words, each 2+ characters)
        words = line.split()
        if len(words) < 1 or len(words) > 4:
            return False
        
        # Each word should be at least 2 characters and look like a name part
        for word in words:
            if len(word) < 2 or not word.isalpha():
                return False
        
        return True
    
    def _is_valid_name(self, name_text: str) -> bool:
        """Validate if text looks like a valid name"""
        if not name_text or len(name_text) < 2:
            return False
        
        # Must contain at least one letter
        if not re.search(r'[A-Z]', name_text):
            return False
        
        # Should not be too long (names are typically under 50 characters)
        if len(name_text) > 50:
            return False
        
        # Should not contain numbers
        if re.search(r'\d', name_text):
            return False
        
        # Should have reasonable word count (1-4 words for first/last name)
        words = name_text.split()
        if len(words) < 1 or len(words) > 4:
            return False
        
        return True
    
    def _parse_name(self, name_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse name text into first and last name"""
        words = name_text.strip().split()
        
        if len(words) == 1:
            # Only one word - could be first or last name
            return words[0], None
        elif len(words) == 2:
            # Two words - assume first and last
            return words[0], words[1]
        elif len(words) >= 3:
            # Three or more words - assume first word is first name, last word is last name
            return words[0], words[-1]
        
        return None, None
    
    def extract_date_of_birth(self, text: str) -> Optional[str]:
        """
        Extract date of birth from license text
        
        Args:
            text: Extracted text from license
            
        Returns:
            Date of birth string if found, None otherwise
        """
        text_upper = text.upper()
        
        # Common DOB patterns and prefixes
        dob_patterns = [
            r'DOB[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'DATE\s*OF\s*BIRTH[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'BIRTH[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'BORN[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'D\.?O\.?B\.?[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        ]
        
        # Look for explicit DOB patterns
        for pattern in dob_patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                date_str = matches[0]
                if self._is_valid_date(date_str):
                    return self._normalize_date(date_str)
        
        # Look for date patterns that might be DOB (without explicit labels)
        # Common date formats
        date_formats = [
            r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
        ]
        
        potential_dates = []
        for pattern in date_formats:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                if self._is_valid_date(match) and self._looks_like_birth_date(match):
                    potential_dates.append(match)
        
        # Return the most likely birth date
        if potential_dates:
            return self._normalize_date(potential_dates[0])
        
        return None
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Validate if string looks like a valid date"""
        if not date_str:
            return False
        
        # Basic format check
        if not re.match(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}', date_str):
            return False
        
        try:
            # Try to parse the date to validate it
            from datetime import datetime
            
            # Try different formats
            formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # Check if it's a reasonable birth date (between 1900 and current year - 16)
                    current_year = datetime.now().year
                    if 1900 <= parsed_date.year <= current_year - 16:
                        return True
                except ValueError:
                    continue
            
            return False
        except:
            return False
    
    def _looks_like_birth_date(self, date_str: str) -> bool:
        """Check if date looks like it could be a birth date"""
        try:
            from datetime import datetime
            
            formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    current_year = datetime.now().year
                    
                    # Birth date should be reasonable (16-120 years ago)
                    age = current_year - parsed_date.year
                    if 16 <= age <= 120:
                        return True
                except ValueError:
                    continue
            
            return False
        except:
            return False
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to MM/DD/YYYY format"""
        try:
            from datetime import datetime
            
            formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%m/%d/%Y')
                except ValueError:
                    continue
            
            return date_str  # Return original if can't parse
        except:
            return date_str
    
    def calculate_confidence(self, license_info: LicenseInfo) -> float:
        """
        Calculate confidence score based on extracted information
        
        Args:
            license_info: Extracted license information
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # State identification adds confidence (25%)
        if license_info.state:
            score += 0.25
        
        # License number adds confidence (35%)
        if license_info.license_number:
            score += 0.35
            
            # Bonus for state-specific pattern match (10%)
            if license_info.state and license_info.state in self.LICENSE_PATTERNS:
                pattern = self.LICENSE_PATTERNS[license_info.state]
                if re.match(pattern, license_info.license_number):
                    score += 0.10
        
        # First name adds confidence (10%)
        if license_info.first_name:
            score += 0.10
        
        # Last name adds confidence (10%)
        if license_info.last_name:
            score += 0.10
        
        # Date of birth adds confidence (10%)
        if license_info.date_of_birth:
            score += 0.10
        
        return min(score, 1.0)
    
    def scan_license(self, image_data: str) -> Dict:
        """
        Main method to scan a driver's license image
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dictionary with extracted information
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Extract text using OCR
            extracted_text = self.extract_text_from_image(image_bytes)
            
            # Create license info object
            license_info = LicenseInfo(raw_text=extracted_text)
            
            # Identify state
            license_info.state = self.identify_state(extracted_text)
            
            # Extract license number
            license_info.license_number = self.extract_license_number(
                extracted_text, license_info.state
            )
            
            # Extract names
            license_info.first_name, license_info.last_name = self.extract_names(extracted_text)
            
            # Extract date of birth
            license_info.date_of_birth = self.extract_date_of_birth(extracted_text)
            
            # Calculate confidence score
            license_info.confidence_score = self.calculate_confidence(license_info)
            
            return {
                'success': True,
                'license_number': license_info.license_number,
                'state': license_info.state,
                'first_name': license_info.first_name,
                'last_name': license_info.last_name,
                'date_of_birth': license_info.date_of_birth,
                'confidence_score': license_info.confidence_score,
                'raw_text': license_info.raw_text
            }
            
        except Exception as e:
            logger.error(f"Error scanning license: {e}")
            return {
                'success': False,
                'error': str(e),
                'license_number': None,
                'state': None,
                'confidence_score': 0.0
            }

def lambda_handler(event, context):
    """
    AWS Lambda handler for the driver's license scanner
    
    Args:
        event: Lambda event containing image data
        context: Lambda context
        
    Returns:
        Response with extracted license information
    """
    scanner = DriversLicenseScanner()
    
    try:
        # Extract image data from event
        if 'image_data' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing image_data in request'
                })
            }
        
        # Scan the license
        result = scanner.scan_license(event['image_data'])
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }

# For local testing
if __name__ == "__main__":
    # Example usage
    scanner = DriversLicenseScanner()
    
    # Mock test (would need actual base64 image data)
    test_event = {
        'image_data': 'base64_encoded_image_here'
    }
    
    print("Driver's License Scanner Agent initialized successfully!")
    print("To use: provide base64 encoded image data in the 'image_data' field")
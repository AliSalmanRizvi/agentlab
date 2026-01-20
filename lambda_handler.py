#!/usr/bin/env python3
"""
AWS Lambda handler for the Driver's License Scanner web service
"""

import json
import base64
import os
import sys
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from lambda_api import LicenseScannerAPI

# Initialize API with region from environment variable
region = os.environ.get('SCANNER_REGION', os.environ.get('AWS_REGION', 'us-east-1'))
api = LicenseScannerAPI(region_name=region)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for the driver's license scanner web service
    
    Args:
        event: Lambda event containing HTTP request data
        context: Lambda context
        
    Returns:
        HTTP response with CORS headers
    """
    try:
        # Extract HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Content-Type': 'application/json'
        }
        
        # Handle preflight OPTIONS requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Route requests
        if path == '/health' and http_method == 'GET':
            return handle_health(cors_headers)
        
        elif path == '/states' and http_method == 'GET':
            return handle_states(cors_headers)
        
        elif path == '/scan' and http_method == 'POST':
            return handle_scan_multipart(event, cors_headers)
        
        elif path == '/scan/base64' and http_method == 'POST':
            return handle_scan_base64(event, cors_headers)
        
        elif path == '/' and http_method == 'GET':
            return handle_root(cors_headers)
        
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({
                    'success': False,
                    'error': f'Endpoint not found: {http_method} {path}'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f'Internal server error: {str(e)}'
            })
        }

def handle_health(headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle health check endpoint"""
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'Driver\'s License Scanner',
            'version': '1.0.0',
            'deployment': 'AWS Lambda'
        })
    }

def handle_states(headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle states endpoint"""
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'states': api.get_supported_states(),
            'count': len(api.get_supported_states())
        })
    }

def handle_scan_base64(event: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle base64 image scanning"""
    try:
        # Parse request body
        body = event.get('body', '{}')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        
        data = json.loads(body)
        
        if 'image_data' not in data:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing image_data in request body'
                })
            }
        
        # Scan the license
        result = api.scan_from_base64(data['image_data'])
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': 'Invalid JSON in request body'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_scan_multipart(event: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle multipart file upload scanning"""
    try:
        # For Lambda, multipart data comes as base64 encoded body
        body = event.get('body', '')
        if not body:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': 'No file data provided'
                })
            }
        
        # If the body is base64 encoded, decode it
        if event.get('isBase64Encoded', False):
            try:
                # Decode the base64 body
                decoded_body = base64.b64decode(body)
                
                # Extract image data from multipart (simplified approach)
                # In a real implementation, you'd parse the multipart boundary
                # For now, assume the decoded body is the image data
                result = api.scan_from_bytes(decoded_body)
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps(result)
                }
                
            except Exception as e:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'error': f'Error processing image: {str(e)}'
                    })
                }
        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                'error': 'Please use base64 endpoint for file uploads in Lambda'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def handle_root(headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle root endpoint with API documentation"""
    api_docs = {
        'service': 'US Driver\'s License Scanner API',
        'version': '1.0.0',
        'deployment': 'AWS Lambda',
        'endpoints': {
            'GET /health': 'Health check',
            'GET /states': 'Get supported US states',
            'POST /scan/base64': 'Scan license from base64 image data',
            'POST /scan': 'Scan license from multipart file upload'
        },
        'usage': {
            'base64_example': {
                'method': 'POST',
                'url': '/scan/base64',
                'headers': {'Content-Type': 'application/json'},
                'body': {'image_data': 'base64_encoded_image_string'}
            }
        },
        'extracted_fields': [
            'license_number',
            'state', 
            'first_name',
            'last_name',
            'date_of_birth',
            'confidence_score'
        ]
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(api_docs, indent=2)
    }
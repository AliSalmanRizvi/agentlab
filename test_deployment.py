#!/usr/bin/env python3
"""
Test script for the deployed AWS API
"""

import requests
import json
import base64
import os
from typing import Dict, Any

def test_api_endpoints(api_url: str) -> None:
    """Test all API endpoints"""
    print(f"🧪 Testing API at: {api_url}")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: States endpoint
    print("\n2. Testing states endpoint...")
    try:
        response = requests.get(f"{api_url}/states", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   States count: {data.get('count')}")
            print(f"   Sample states: {data.get('states', [])[:5]}...")
            print("   ✅ States endpoint passed")
        else:
            print(f"   ❌ States endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ States endpoint error: {e}")
    
    # Test 3: API documentation
    print("\n3. Testing API documentation...")
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Endpoints: {len(data.get('endpoints', {}))}")
            print("   ✅ API documentation passed")
        else:
            print(f"   ❌ API documentation failed: {response.text}")
    except Exception as e:
        print(f"   ❌ API documentation error: {e}")
    
    # Test 4: Base64 scan endpoint (with mock data)
    print("\n4. Testing base64 scan endpoint...")
    try:
        # Create a small test image (1x1 pixel PNG)
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        
        payload = {
            "image_data": test_image_b64
        }
        
        response = requests.post(
            f"{api_url}/scan/base64",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('success'):
                print(f"   License: {data.get('license_number', 'Not found')}")
                print(f"   State: {data.get('state', 'Not found')}")
                print(f"   First Name: {data.get('first_name', 'Not found')}")
                print(f"   Last Name: {data.get('last_name', 'Not found')}")
                print(f"   DOB: {data.get('date_of_birth', 'Not found')}")
                print(f"   Confidence: {data.get('confidence_score', 0):.2%}")
            print("   ✅ Base64 scan endpoint working (mock data)")
        else:
            print(f"   ⚠️ Base64 scan returned: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Base64 scan error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API testing completed!")
    print(f"\n📋 Usage Examples:")
    print(f"   Health Check: curl {api_url}/health")
    print(f"   Get States: curl {api_url}/states")
    print(f"   API Docs: curl {api_url}/")
    print(f"   Scan License: curl -X POST {api_url}/scan/base64 \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"image_data\": \"base64_encoded_image\"}}'")

def create_test_html(api_url: str) -> None:
    """Create a test HTML page for the API"""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>License Scanner API Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .container {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .result {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .error {{ background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        input[type="file"] {{ margin: 10px 0; }}
        button {{ background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #005a87; }}
        .info {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>🆔 US Driver's License Scanner API</h1>
    
    <div class="info">
        <h3>AWS Deployed API Test Page</h3>
        <p><strong>API URL:</strong> {api_url}</p>
        <p><strong>Deployment:</strong> AWS Lambda + API Gateway</p>
        <p><strong>Features:</strong> Field code-based extraction (Fields 1, 2, 7)</p>
    </div>
    
    <div class="container">
        <h3>Upload License Image</h3>
        <input type="file" id="imageFile" accept="image/*" required>
        <br>
        <button onclick="scanLicense()">Scan License</button>
        
        <div id="result"></div>
    </div>
    
    <div class="container">
        <h3>API Endpoints</h3>
        <ul>
            <li><a href="{api_url}/" target="_blank">GET / - API Documentation</a></li>
            <li><a href="{api_url}/health" target="_blank">GET /health - Health Check</a></li>
            <li><a href="{api_url}/states" target="_blank">GET /states - Supported States</a></li>
            <li><code>POST /scan/base64</code> - Scan base64 image</li>
        </ul>
    </div>

    <script>
        async function scanLicense() {{
            const fileInput = document.getElementById('imageFile');
            const resultDiv = document.getElementById('result');
            
            if (!fileInput.files[0]) {{
                resultDiv.innerHTML = '<div class="error">Please select an image file</div>';
                return;
            }}
            
            resultDiv.innerHTML = '<div class="info">Scanning license...</div>';
            
            try {{
                // Convert file to base64
                const file = fileInput.files[0];
                const base64 = await fileToBase64(file);
                
                const response = await fetch('{api_url}/scan/base64', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        image_data: base64.split(',')[1] // Remove data:image/...;base64, prefix
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h4>✅ Scan Results</h4>
                            <p><strong>License Number:</strong> ${{result.license_number || 'Not found'}}</p>
                            <p><strong>State:</strong> ${{result.state || 'Not found'}}</p>
                            <p><strong>First Name:</strong> ${{result.first_name || 'Not found'}}</p>
                            <p><strong>Last Name:</strong> ${{result.last_name || 'Not found'}}</p>
                            <p><strong>Date of Birth:</strong> ${{result.date_of_birth || 'Not found'}}</p>
                            <p><strong>Confidence:</strong> ${{(result.confidence_score * 100).toFixed(1)}}%</p>
                        </div>
                    `;
                }} else {{
                    resultDiv.innerHTML = `<div class="error">❌ Error: ${{result.error}}</div>`;
                }}
            }} catch (error) {{
                resultDiv.innerHTML = `<div class="error">❌ Network error: ${{error.message}}</div>`;
            }}
        }}
        
        function fileToBase64(file) {{
            return new Promise((resolve, reject) => {{
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => resolve(reader.result);
                reader.onerror = error => reject(error);
            }});
        }}
    </script>
</body>
</html>"""
    
    with open('test_api.html', 'w') as f:
        f.write(html_content)
    
    print(f"📄 Created test_api.html - Open this file in a browser to test the API")

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test deployed License Scanner API')
    parser.add_argument('api_url', help='API Gateway URL')
    parser.add_argument('--create-html', action='store_true', help='Create test HTML page')
    
    args = parser.parse_args()
    
    # Test API endpoints
    test_api_endpoints(args.api_url)
    
    # Create test HTML if requested
    if args.create_html:
        create_test_html(args.api_url)

if __name__ == "__main__":
    main()
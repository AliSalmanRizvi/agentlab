#!/usr/bin/env python3
"""
Driver's License Scanner Web Service

A simple Flask web service for the driver's license scanner agent.
Provides REST API endpoints for scanning licenses.
"""

from flask import Flask, request, jsonify, render_template_string
from .api import LicenseScannerAPI
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize API with region (can be overridden by environment variable)
region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
api = LicenseScannerAPI(region_name=region)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Driver's License Scanner</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .result { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .error { background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        input[type="file"] { margin: 10px 0; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a87; }
        .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🆔 US Driver's License Scanner</h1>
    
    <div class="info">
        <h3>How to use:</h3>
        <ol>
            <li>Take a clear photo of a US driver's license</li>
            <li>Upload the image using the form below</li>
            <li>The scanner will extract license number, state, names, and date of birth</li>
        </ol>
        <p><strong>Supported:</strong> All 50 US states + DC</p>
        <p><strong>Extracts:</strong> License number, state, first name, last name, date of birth</p>
        <p><strong>Privacy:</strong> Images are processed locally and not stored</p>
    </div>
    
    <div class="container">
        <h3>Upload License Image</h3>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" id="imageFile" accept="image/*" required>
            <br>
            <button type="submit">Scan License</button>
        </form>
        
        <div id="result"></div>
    </div>
    
    <div class="container">
        <h3>API Endpoints</h3>
        <ul>
            <li><code>POST /scan</code> - Upload image file for scanning</li>
            <li><code>POST /scan/base64</code> - Send base64 encoded image</li>
            <li><code>GET /states</code> - Get supported states</li>
            <li><code>GET /health</code> - Health check</li>
        </ul>
    </div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('imageFile');
            const resultDiv = document.getElementById('result');
            
            if (!fileInput.files[0]) {
                resultDiv.innerHTML = '<div class="error">Please select an image file</div>';
                return;
            }
            
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            
            resultDiv.innerHTML = '<div class="info">Scanning license...</div>';
            
            try {
                const response = await fetch('/scan', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h4>✅ Scan Results</h4>
                            <p><strong>License Number:</strong> ${result.license_number || 'Not found'}</p>
                            <p><strong>State:</strong> ${result.state || 'Not found'}</p>
                            <p><strong>First Name:</strong> ${result.first_name || 'Not found'}</p>
                            <p><strong>Last Name:</strong> ${result.last_name || 'Not found'}</p>
                            <p><strong>Date of Birth:</strong> ${result.date_of_birth || 'Not found'}</p>
                            <p><strong>Confidence:</strong> ${(result.confidence_score * 100).toFixed(1)}%</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Network error: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan_license():
    """
    Scan driver's license from uploaded image file
    
    Returns:
        JSON response with scan results
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read image bytes
        image_bytes = file.read()
        
        # Scan the license
        result = api.scan_from_bytes(image_bytes)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in scan endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/scan/base64', methods=['POST'])
def scan_license_base64():
    """
    Scan driver's license from base64 encoded image
    
    Expected JSON payload:
    {
        "image_data": "base64_encoded_image_string"
    }
    
    Returns:
        JSON response with scan results
    """
    try:
        data = request.get_json()
        
        if not data or 'image_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing image_data in request body'
            }), 400
        
        # Scan the license
        result = api.scan_from_base64(data['image_data'])
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in base64 scan endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/states', methods=['GET'])
def get_states():
    """
    Get list of supported US states
    
    Returns:
        JSON list of state abbreviations
    """
    return jsonify({
        'states': api.get_supported_states(),
        'count': len(api.get_supported_states())
    })

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON response with service status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Driver\'s License Scanner',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Driver's License Scanner Web Service...")
    print("📱 Web interface: http://localhost:5000")
    print("🔗 API endpoints:")
    print("   POST /scan - Upload image file")
    print("   POST /scan/base64 - Send base64 image")
    print("   GET /states - Get supported states")
    print("   GET /health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
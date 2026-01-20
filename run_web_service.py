#!/usr/bin/env python3
"""
Entry point to run the Driver's License Scanner Web Service
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from license_scanner.web_service import app

if __name__ == '__main__':
    print("🚀 Starting Driver's License Scanner Web Service...")
    print("📱 Web interface: http://localhost:8080")
    print("🔗 API endpoints:")
    print("   POST /scan - Upload image file")
    print("   POST /scan/base64 - Send base64 image")
    print("   GET /states - Get supported states")
    print("   GET /health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
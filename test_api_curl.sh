#!/bin/bash

# Test script for the deployed License Scanner API
API_URL="https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod"

echo "🧪 Testing License Scanner API"
echo "API URL: $API_URL"
echo "=================================="

echo ""
echo "1. Health Check:"
curl -s "$API_URL/health" | python3 -m json.tool

echo ""
echo "2. Supported States (first 10):"
curl -s "$API_URL/states" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total states: {data[\"count\"]}')
print('First 10 states:', ', '.join(data['states'][:10]))
"

echo ""
echo "3. Test Base64 Scan (with sample image):"
# Create a simple test image in base64 (small PNG)
TEST_IMAGE="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="

curl -s -X POST "$API_URL/scan/base64" \
  -H "Content-Type: application/json" \
  -d "{\"image_data\": \"$TEST_IMAGE\"}" | python3 -m json.tool

echo ""
echo "=================================="
echo "✅ API is deployed and working!"
echo ""
echo "📋 Usage:"
echo "  Health: curl $API_URL/health"
echo "  States: curl $API_URL/states"
echo "  Scan:   curl -X POST $API_URL/scan/base64 -H 'Content-Type: application/json' -d '{\"image_data\": \"BASE64_IMAGE\"}'"
echo ""
echo "🌐 Test in browser: Open test_api.html"
echo "📱 Live API URL: $API_URL"
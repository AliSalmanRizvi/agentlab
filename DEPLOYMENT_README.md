# 🚀 US Driver's License Scanner - AWS Deployment

## ✅ **SUCCESSFULLY DEPLOYED!**

Your US Driver's License Scanner is now live on AWS with field code-based name extraction!

---

## 🌐 **Live API URL**
```
https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod
```

---

## 🧪 **Test the API**

### **Quick Test**
```bash
./test_api_curl.sh
```

### **Browser Test**
Open `test_api.html` in your browser for an interactive interface.

### **Manual cURL Tests**

**Health Check:**
```bash
curl https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod/health
```

**Get Supported States:**
```bash
curl https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod/states
```

**Scan License (Base64):**
```bash
curl -X POST https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod/scan/base64 \
  -H "Content-Type: application/json" \
  -d '{"image_data": "YOUR_BASE64_IMAGE_HERE"}'
```

---

## 📊 **API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/states` | List supported US states |
| `POST` | `/scan/base64` | Scan license from base64 image |

---

## 🎯 **Field Code Extraction**

The scanner uses standardized driver's license field codes:
- **Field 1**: Last Name
- **Field 2**: First Name  
- **Field 7**: Date of Birth
- **Field 8**: License Number (varies by state)

---

## 📋 **Response Format**

```json
{
  "success": true,
  "license_number": "123456789",
  "state": "CT",
  "first_name": "JOHN",
  "last_name": "DOE",
  "date_of_birth": "01/15/1990",
  "confidence_score": 0.90,
  "raw_text": "..."
}
```

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│  Lambda Function │───▶│  AWS Textract   │
│  (REST API)     │    │  (Python 3.9)   │    │   (OCR Service) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Components:**
- **API Gateway**: REST API with CORS enabled
- **Lambda Function**: Serverless compute with field code extraction
- **AWS Textract**: OCR service for text extraction
- **IAM Role**: Permissions for Textract access

---

## 💰 **Cost Estimate**

**AWS Lambda:**
- Free tier: 1M requests/month
- After free tier: $0.20 per 1M requests

**AWS Textract:**
- $1.50 per 1,000 pages processed

**API Gateway:**
- Free tier: 1M API calls/month
- After free tier: $3.50 per 1M calls

**Estimated cost for 1,000 license scans/month: ~$2-3**

---

## 🔧 **Deployment Details**

**AWS Resources Created:**
- Lambda Function: `license-scanner-api`
- IAM Role: `license-scanner-lambda-role`
- API Gateway: `license-scanner-api`
- Lambda Layer: `license-scanner-dependencies`

**Region:** `us-east-1`

---

## 🚀 **Features**

✅ **Field Code Recognition** - Uses standardized DL field codes  
✅ **All 50 US States + DC** - Complete coverage  
✅ **High Accuracy** - Field-based extraction vs pattern matching  
✅ **Serverless** - Auto-scaling, pay-per-use  
✅ **CORS Enabled** - Works from web browsers  
✅ **Error Handling** - Comprehensive validation  
✅ **Multiple Formats** - JPEG, PNG, PDF support  

---

## 📱 **Integration Examples**

### **JavaScript (Browser)**
```javascript
async function scanLicense(base64Image) {
  const response = await fetch('https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod/scan/base64', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_data: base64Image })
  });
  return await response.json();
}
```

### **Python**
```python
import requests
import base64

def scan_license(image_path):
    with open(image_path, 'rb') as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    response = requests.post(
        'https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod/scan/base64',
        json={'image_data': image_b64}
    )
    return response.json()
```

### **cURL**
```bash
# Convert image to base64 and scan
IMAGE_B64=$(base64 -i license.jpg)
curl -X POST https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod/scan/base64 \
  -H "Content-Type: application/json" \
  -d "{\"image_data\": \"$IMAGE_B64\"}"
```

---

## 🔍 **Monitoring**

**CloudWatch Logs:**
```bash
aws logs tail /aws/lambda/license-scanner-api --follow
```

**Metrics:**
- Function duration
- Error rate  
- Invocation count
- Textract API calls

---

## 🛠️ **Troubleshooting**

**Common Issues:**

1. **"Invalid image format"**
   - Ensure image is JPEG, PNG, or PDF
   - Check base64 encoding is correct

2. **"Internal server error"**
   - Check CloudWatch logs
   - Verify AWS credentials/permissions

3. **High latency**
   - Cold start delay (first request)
   - Consider provisioned concurrency for production

---

## 🎉 **Success!**

Your US Driver's License Scanner is now deployed and ready to use! The API can extract:

- ✅ License numbers (all 50 states + DC)
- ✅ State identification  
- ✅ First and last names (field code-based)
- ✅ Date of birth (field code-based)
- ✅ Confidence scoring

**Live API:** https://6r16jrg77d.execute-api.us-east-1.amazonaws.com/prod

**Test Interface:** Open `test_api.html` in your browser

---

*Deployment completed successfully! 🚀*
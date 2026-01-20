# US Driver's License Scanner - Project Structure

```
us-drivers-license-scanner/
├── 📁 src/                          # Source code
│   └── 📁 license_scanner/          # Main package
│       ├── __init__.py              # Package initialization
│       ├── scanner.py               # Core scanner with AWS Textract
│       ├── api.py                   # User-friendly API wrapper
│       └── web_service.py           # Flask web service
│
├── 📁 tests/                        # Test suite
│   ├── __init__.py                  # Test package init
│   ├── test_scanner.py              # Main test suite
│   └── test_ct_extraction.py        # Connecticut-specific tests
│
├── 📁 deployment/                   # Deployment scripts
│   └── deploy_lambda.py             # AWS Lambda deployment
│
├── 📁 docs/                         # Documentation (empty for now)
├── 📁 examples/                     # Usage examples (empty for now)
├── 📁 scripts/                      # Utility scripts (empty for now)
│
├── 🚀 Entry Points:
├── run_web_service.py               # Start web interface
├── scan_license.py                  # CLI scanner
├── run_tests.py                     # Run all tests
├── setup.py                         # AWS setup helper
│
├── 📄 Configuration:
├── requirements.txt                 # Python dependencies
├── .gitignore                      # Git exclusions
│
├── 📚 Documentation:
├── README.md                       # Complete usage guide
├── AGENT_SUMMARY.md                # Project overview
├── PROJECT_STRUCTURE.md            # This file
│
└── 🛠️ Utilities:
    ├── setup_aws.py               # AWS configuration helper
    └── demo_extraction.py         # Demo script
```

## 🚀 Quick Start Commands

### Run Web Interface
```bash
python3 run_web_service.py
# Open http://localhost:5000
```

### Scan a License (CLI)
```bash
python3 scan_license.py path/to/license.jpg
python3 scan_license.py path/to/license.jpg --json
```

### Run Tests
```bash
python3 run_tests.py
```

### Setup AWS
```bash
python3 setup.py
```

### Deploy to Lambda
```bash
python3 deployment/deploy_lambda.py
```

## 📦 Package Structure

The main package `src/license_scanner/` contains:

- **`scanner.py`**: Core `DriversLicenseScanner` class with AWS Textract integration
- **`api.py`**: `LicenseScannerAPI` wrapper for easy usage
- **`web_service.py`**: Flask web service with REST API endpoints

## 🧪 Testing

Tests are organized in the `tests/` directory:

- **`test_scanner.py`**: Comprehensive test suite with mocking
- **`test_ct_extraction.py`**: Connecticut-specific extraction tests

## 🚀 Deployment

Deployment scripts in `deployment/` directory:

- **`deploy_lambda.py`**: Automated AWS Lambda deployment with IAM setup

## 📋 Entry Points

Easy-to-use entry point scripts in the root directory:

- **`run_web_service.py`**: Start the web interface
- **`scan_license.py`**: Command-line scanner
- **`run_tests.py`**: Execute all tests
- **`setup.py`**: AWS configuration helper

This structure provides:
✅ Clean separation of concerns
✅ Easy imports and package management
✅ Simple entry points for different use cases
✅ Organized testing structure
✅ Clear deployment process
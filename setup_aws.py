#!/usr/bin/env python3
"""
AWS Setup Helper for Driver's License Scanner

This script helps configure AWS credentials and region for the scanner.
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        # Try to create a client and make a simple call
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS credentials are configured")
        print(f"   Account ID: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role: {identity.get('Arn', 'Unknown')}")
        return True
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        return False
    except Exception as e:
        print(f"❌ Error checking AWS credentials: {e}")
        return False

def check_textract_permissions():
    """Check if the current credentials have Textract permissions"""
    try:
        textract = boto3.client('textract', region_name='us-east-1')
        # Try to make a simple call (this will fail but we can check the error)
        try:
            textract.detect_document_text(Document={'Bytes': b'fake'})
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['InvalidParameterException', 'UnsupportedDocumentException']:
                print("✅ Textract permissions are configured correctly")
                return True
            elif error_code == 'AccessDenied':
                print("❌ Access denied to Textract service")
                return False
            else:
                print(f"⚠️ Unexpected Textract error: {error_code}")
                print("✅ Textract permissions appear to be working (can access service)")
                return True
        except Exception as e:
            print(f"❌ Error testing Textract permissions: {e}")
            return False
    except Exception as e:
        print(f"❌ Error creating Textract client: {e}")
        return False

def get_available_regions():
    """Get list of available AWS regions for Textract"""
    textract_regions = [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1',
        'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2',
        'ap-south-1', 'ca-central-1'
    ]
    return textract_regions

def setup_region():
    """Help user set up AWS region"""
    current_region = os.environ.get('AWS_DEFAULT_REGION')
    
    if current_region:
        print(f"📍 Current AWS region: {current_region}")
    else:
        print("📍 No AWS region set")
    
    print("\n🌍 Available Textract regions:")
    regions = get_available_regions()
    for i, region in enumerate(regions, 1):
        marker = " (current)" if region == current_region else ""
        print(f"   {i:2d}. {region}{marker}")
    
    print(f"\n💡 Recommended regions:")
    print(f"   • us-east-1 (N. Virginia) - Most services, lowest latency for US East")
    print(f"   • us-west-2 (Oregon) - Good for US West")
    print(f"   • eu-west-1 (Ireland) - Good for Europe")
    
    return regions

def set_environment_region(region):
    """Set AWS region in environment variable"""
    os.environ['AWS_DEFAULT_REGION'] = region
    print(f"✅ Set AWS_DEFAULT_REGION to {region} for this session")
    print(f"\n💡 To make this permanent, add to your shell profile:")
    print(f"   export AWS_DEFAULT_REGION={region}")

def main():
    """Main setup function"""
    print("🚀 AWS Setup Helper for Driver's License Scanner")
    print("=" * 50)
    
    # Check credentials
    print("\n1️⃣ Checking AWS credentials...")
    if not check_aws_credentials():
        print("\n❌ AWS credentials not configured!")
        print("\n📋 To configure AWS credentials, run:")
        print("   aws configure")
        print("\n   Or set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        return
    
    # Check region
    print("\n2️⃣ Checking AWS region...")
    regions = setup_region()
    
    current_region = os.environ.get('AWS_DEFAULT_REGION')
    if not current_region:
        print("\n⚠️ No AWS region configured!")
        
        # Ask user to select region
        try:
            choice = input(f"\nSelect a region (1-{len(regions)}) or press Enter for us-east-1: ").strip()
            if not choice:
                selected_region = 'us-east-1'
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(regions):
                    selected_region = regions[idx]
                else:
                    print("Invalid choice, using us-east-1")
                    selected_region = 'us-east-1'
            
            set_environment_region(selected_region)
            
        except (ValueError, KeyboardInterrupt):
            print("\nUsing default region: us-east-1")
            set_environment_region('us-east-1')
    
    # Check Textract permissions
    print("\n3️⃣ Checking Textract permissions...")
    if not check_textract_permissions():
        print("\n❌ Textract permissions not configured!")
        print("\n📋 Required IAM policy:")
        print("""
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "textract:DetectDocumentText"
      ],
      "Resource": "*"
    }
  ]
}""")
        return
    
    print("\n" + "=" * 50)
    print("🎉 AWS setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run tests: python test_scanner.py")
    print("   2. Try CLI: python license_scanner_api.py image.jpg")
    print("   3. Start web service: python web_service.py")

if __name__ == "__main__":
    main()
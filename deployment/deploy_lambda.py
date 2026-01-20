#!/usr/bin/env python3
"""
AWS Lambda Deployment Script for Driver's License Scanner

This script helps deploy the scanner agent to AWS Lambda.
"""

import json
import zipfile
import boto3
import os
from pathlib import Path

class LambdaDeployer:
    """Helper class for deploying to AWS Lambda"""
    
    def __init__(self, function_name="drivers-license-scanner"):
        """Initialize the deployer"""
        self.function_name = function_name
        self.lambda_client = boto3.client('lambda')
        self.iam_client = boto3.client('iam')
    
    def create_deployment_package(self):
        """Create deployment ZIP package"""
        print("📦 Creating deployment package...")
        
        files_to_include = [
            'drivers_license_scanner.py',
            'requirements.txt'
        ]
        
        zip_path = f"{self.function_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in files_to_include:
                if Path(file_name).exists():
                    zipf.write(file_name)
                    print(f"  ✅ Added {file_name}")
                else:
                    print(f"  ⚠️ Warning: {file_name} not found")
        
        print(f"📦 Package created: {zip_path}")
        return zip_path
    
    def create_iam_role(self):
        """Create IAM role for Lambda function"""
        print("🔐 Creating IAM role...")
        
        role_name = f"{self.function_name}-role"
        
        # Trust policy for Lambda
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Execution policy with Textract permissions
        execution_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "textract:DetectDocumentText"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Create role
            role_response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"IAM role for {self.function_name} Lambda function"
            )
            
            # Attach execution policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName=f"{role_name}-policy",
                PolicyDocument=json.dumps(execution_policy)
            )
            
            role_arn = role_response['Role']['Arn']
            print(f"  ✅ Created role: {role_arn}")
            return role_arn
            
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            # Role already exists, get its ARN
            role_response = self.iam_client.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"  ℹ️ Using existing role: {role_arn}")
            return role_arn
    
    def create_lambda_function(self, zip_path, role_arn):
        """Create or update Lambda function"""
        print("🚀 Creating Lambda function...")
        
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        try:
            # Try to create new function
            response = self.lambda_client.create_function(
                FunctionName=self.function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='drivers_license_scanner.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='US Driver\'s License Scanner Agent',
                Timeout=30,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'LOG_LEVEL': 'INFO'
                    }
                }
            )
            
            print(f"  ✅ Created function: {response['FunctionArn']}")
            return response['FunctionArn']
            
        except self.lambda_client.exceptions.ResourceConflictException:
            # Function exists, update it
            print("  ℹ️ Function exists, updating code...")
            
            response = self.lambda_client.update_function_code(
                FunctionName=self.function_name,
                ZipFile=zip_content
            )
            
            print(f"  ✅ Updated function: {response['FunctionArn']}")
            return response['FunctionArn']
    
    def test_function(self):
        """Test the deployed function"""
        print("🧪 Testing deployed function...")
        
        # Create test event
        test_event = {
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                Payload=json.dumps(test_event)
            )
            
            result = json.loads(response['Payload'].read())
            print(f"  📄 Test response: {result}")
            
            if response['StatusCode'] == 200:
                print("  ✅ Function test successful!")
            else:
                print("  ⚠️ Function test returned non-200 status")
                
        except Exception as e:
            print(f"  ❌ Function test failed: {e}")
    
    def deploy(self):
        """Full deployment process"""
        print(f"🚀 Deploying {self.function_name} to AWS Lambda")
        print("=" * 50)
        
        try:
            # Step 1: Create deployment package
            zip_path = self.create_deployment_package()
            
            # Step 2: Create IAM role
            role_arn = self.create_iam_role()
            
            # Wait a moment for role to propagate
            import time
            print("⏳ Waiting for IAM role to propagate...")
            time.sleep(10)
            
            # Step 3: Create/update Lambda function
            function_arn = self.create_lambda_function(zip_path, role_arn)
            
            # Step 4: Test function
            self.test_function()
            
            print("\n" + "=" * 50)
            print("🎉 Deployment completed successfully!")
            print(f"📍 Function ARN: {function_arn}")
            print(f"🔧 Function Name: {self.function_name}")
            
            print("\n📋 Next steps:")
            print("  1. Test with real image data")
            print("  2. Set up API Gateway (optional)")
            print("  3. Configure monitoring and alerts")
            
            # Clean up
            os.remove(zip_path)
            print(f"🧹 Cleaned up {zip_path}")
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            print("Please check your AWS credentials and permissions.")

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Driver\'s License Scanner to AWS Lambda')
    parser.add_argument('--function-name', default='drivers-license-scanner',
                       help='Lambda function name (default: drivers-license-scanner)')
    
    args = parser.parse_args()
    
    # Check AWS credentials
    try:
        boto3.client('sts').get_caller_identity()
        print("✅ AWS credentials configured")
    except Exception as e:
        print(f"❌ AWS credentials not configured: {e}")
        print("Please run 'aws configure' first")
        return
    
    # Deploy
    deployer = LambdaDeployer(args.function_name)
    deployer.deploy()

if __name__ == "__main__":
    main()
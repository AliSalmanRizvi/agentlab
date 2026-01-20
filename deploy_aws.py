#!/usr/bin/env python3
"""
AWS Deployment script for the Driver's License Scanner
"""

import boto3
import json
import zipfile
import os
import time
from typing import Dict, Any

class AWSDeployer:
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.apigateway_client = boto3.client('apigateway', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
        # Configuration
        self.function_name = 'license-scanner-api'
        self.role_name = 'license-scanner-lambda-role'
        self.api_name = 'license-scanner-api'
        
    def create_deployment_package(self) -> str:
        """Create deployment ZIP package"""
        print("📦 Creating deployment package...")
        
        zip_filename = 'license-scanner-deployment.zip'
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add Lambda handler
            zipf.write('lambda_handler.py')
            
            # Add Lambda-specific API
            zipf.write('lambda_api.py')
            
            # Add source code
            for root, dirs, files in os.walk('src'):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        arcname = file_path
                        
                        # Skip the regular api.py file (has PIL dependency)
                        if file == 'api.py':
                            continue
                        
                        # Replace __init__.py with Lambda version
                        if file == '__init__.py' and 'license_scanner' in root:
                            # Use Lambda-specific __init__.py
                            lambda_init_path = os.path.join(root, '__init___lambda.py')
                            if os.path.exists(lambda_init_path):
                                zipf.write(lambda_init_path, arcname)
                                continue
                        
                        zipf.write(file_path, arcname)
            
            print(f"✅ Created {zip_filename}")
        
        return zip_filename
    
    def create_iam_role(self) -> str:
        """Create IAM role for Lambda function"""
        print("🔐 Creating IAM role...")
        
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
        
        try:
            # Try to get existing role
            response = self.iam_client.get_role(RoleName=self.role_name)
            role_arn = response['Role']['Arn']
            print(f"✅ Using existing role: {role_arn}")
            return role_arn
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create new role
            response = self.iam_client.create_role(
                RoleName=self.role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='IAM role for License Scanner Lambda function'
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach basic Lambda execution policy
            self.iam_client.attach_role_policy(
                RoleName=self.role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach Textract policy
            textract_policy = {
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
            }
            
            self.iam_client.put_role_policy(
                RoleName=self.role_name,
                PolicyName='TextractAccess',
                PolicyDocument=json.dumps(textract_policy)
            )
            
            print(f"✅ Created IAM role: {role_arn}")
            
            # Wait for role to be available
            print("⏳ Waiting for IAM role to be available...")
            time.sleep(5)
            
            return role_arn
    
    def create_lambda_function(self, zip_filename: str, role_arn: str) -> str:
        """Create or update Lambda function"""
        print("🚀 Creating/updating Lambda function...")
        
        with open(zip_filename, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        try:
            # Try to update existing function
            response = self.lambda_client.update_function_code(
                FunctionName=self.function_name,
                ZipFile=zip_content
            )
            
            # Wait for update to complete
            print("⏳ Waiting for function update to complete...")
            waiter = self.lambda_client.get_waiter('function_updated')
            waiter.wait(FunctionName=self.function_name)
            
            # Update configuration
            self.lambda_client.update_function_configuration(
                FunctionName=self.function_name,
                Runtime='python3.9',
                Handler='lambda_handler.lambda_handler',
                Timeout=30,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'SCANNER_REGION': self.region
                    }
                }
            )
            
            function_arn = response['FunctionArn']
            print(f"✅ Updated Lambda function: {function_arn}")
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            # Create new function
            response = self.lambda_client.create_function(
                FunctionName=self.function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_handler.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='US Driver\'s License Scanner API',
                Timeout=30,
                MemorySize=512,
                Environment={
                    'Variables': {
                        'SCANNER_REGION': self.region
                    }
                }
            )
            
            function_arn = response['FunctionArn']
            print(f"✅ Created Lambda function: {function_arn}")
        
        return function_arn
    
    def create_api_gateway(self, function_arn: str) -> str:
        """Create API Gateway and connect to Lambda"""
        print("🌐 Creating API Gateway...")
        
        # Get account ID from function ARN
        account_id = function_arn.split(':')[4]
        
        try:
            # Get existing API
            apis = self.apigateway_client.get_rest_apis()
            existing_api = None
            
            for api in apis['items']:
                if api['name'] == self.api_name:
                    existing_api = api
                    break
            
            if existing_api:
                api_id = existing_api['id']
                print(f"✅ Using existing API Gateway: {api_id}")
            else:
                # Create new API
                response = self.apigateway_client.create_rest_api(
                    name=self.api_name,
                    description='US Driver\'s License Scanner API',
                    endpointConfiguration={'types': ['REGIONAL']}
                )
                
                api_id = response['id']
                print(f"✅ Created API Gateway: {api_id}")
            
            # Get root resource
            resources = self.apigateway_client.get_resources(restApiId=api_id)
            root_resource_id = None
            
            for resource in resources['items']:
                if resource['path'] == '/':
                    root_resource_id = resource['id']
                    break
            
            # Create proxy resource for all paths
            try:
                proxy_resource = self.apigateway_client.create_resource(
                    restApiId=api_id,
                    parentId=root_resource_id,
                    pathPart='{proxy+}'
                )
                proxy_resource_id = proxy_resource['id']
            except self.apigateway_client.exceptions.ConflictException:
                # Resource already exists
                for resource in resources['items']:
                    if resource.get('pathPart') == '{proxy+}':
                        proxy_resource_id = resource['id']
                        break
            
            # Create ANY method for proxy resource
            try:
                self.apigateway_client.put_method(
                    restApiId=api_id,
                    resourceId=proxy_resource_id,
                    httpMethod='ANY',
                    authorizationType='NONE'
                )
            except self.apigateway_client.exceptions.ConflictException:
                pass  # Method already exists
            
            # Create integration
            lambda_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{function_arn}/invocations"
            
            try:
                self.apigateway_client.put_integration(
                    restApiId=api_id,
                    resourceId=proxy_resource_id,
                    httpMethod='ANY',
                    type='AWS_PROXY',
                    integrationHttpMethod='POST',
                    uri=lambda_uri
                )
            except self.apigateway_client.exceptions.ConflictException:
                pass  # Integration already exists
            
            # Add Lambda permission for API Gateway
            try:
                source_arn = f"arn:aws:execute-api:{self.region}:{account_id}:{api_id}/*/*"
                self.lambda_client.add_permission(
                    FunctionName=self.function_name,
                    StatementId='api-gateway-invoke',
                    Action='lambda:InvokeFunction',
                    Principal='apigateway.amazonaws.com',
                    SourceArn=source_arn
                )
            except self.lambda_client.exceptions.ResourceConflictException:
                pass  # Permission already exists
            
            # Deploy API
            deployment = self.apigateway_client.create_deployment(
                restApiId=api_id,
                stageName='prod',
                description='Production deployment'
            )
            
            # Construct API URL
            api_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod"
            
            print(f"✅ API Gateway deployed: {api_url}")
            return api_url
            
        except Exception as e:
            print(f"❌ Error creating API Gateway: {e}")
            raise
    
    def deploy(self) -> Dict[str, str]:
        """Deploy the complete application"""
        print("🚀 Starting AWS deployment...")
        print("=" * 50)
        
        try:
            # Step 1: Create deployment package
            zip_filename = self.create_deployment_package()
            
            # Step 2: Create IAM role
            role_arn = self.create_iam_role()
            
            # Step 3: Create Lambda function
            function_arn = self.create_lambda_function(zip_filename, role_arn)
            
            # Step 4: Create API Gateway
            api_url = self.create_api_gateway(function_arn)
            
            # Clean up
            os.remove(zip_filename)
            
            print("\n" + "=" * 50)
            print("🎉 Deployment completed successfully!")
            print(f"📱 API URL: {api_url}")
            print(f"🔍 Health Check: {api_url}/health")
            print(f"🗺️ States: {api_url}/states")
            print(f"📄 API Docs: {api_url}/")
            
            return {
                'api_url': api_url,
                'function_arn': function_arn,
                'role_arn': role_arn
            }
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            raise

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy License Scanner to AWS')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    deployer = AWSDeployer(region=args.region)
    result = deployer.deploy()
    
    print("\n📋 Deployment Summary:")
    print(f"  API URL: {result['api_url']}")
    print(f"  Function ARN: {result['function_arn']}")
    print(f"  Role ARN: {result['role_arn']}")

if __name__ == "__main__":
    main()
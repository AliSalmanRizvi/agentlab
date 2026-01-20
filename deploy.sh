#!/bin/bash

# AWS Deployment Script for License Scanner
echo "🚀 Deploying License Scanner to AWS..."
echo "========================================"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import boto3; print('✅ boto3 available')" || {
    echo "❌ boto3 not found. Installing..."
    pip3 install boto3
}

# Run deployment
echo "🚀 Starting deployment..."
python3 deploy_aws.py --region us-east-1

# Check deployment status
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the API using the provided URL"
    echo "2. Run: python3 test_deployment.py <API_URL>"
    echo "3. Create test page: python3 test_deployment.py <API_URL> --create-html"
    echo ""
else
    echo "❌ Deployment failed. Check the error messages above."
    exit 1
fi
#!/usr/bin/env python3
"""
Create Lambda layer with dependencies
"""

import os
import subprocess
import zipfile
import boto3

def create_dependencies_layer():
    """Create a Lambda layer with required dependencies"""
    print("📦 Creating Lambda layer with dependencies...")
    
    # Create temporary directory for layer
    layer_dir = "lambda_layer"
    python_dir = os.path.join(layer_dir, "python")
    
    # Clean up existing directory
    if os.path.exists(layer_dir):
        subprocess.run(["rm", "-rf", layer_dir])
    
    os.makedirs(python_dir, exist_ok=True)
    
    # Install dependencies to the layer directory
    print("📥 Installing dependencies...")
    subprocess.run([
        "pip3", "install", 
        "Pillow==10.0.0",
        "requests==2.31.0",
        "-t", python_dir
    ], check=True)
    
    # Create layer zip
    layer_zip = "lambda_layer.zip"
    print(f"🗜️ Creating {layer_zip}...")
    
    with zipfile.ZipFile(layer_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, layer_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    subprocess.run(["rm", "-rf", layer_dir])
    
    print(f"✅ Created layer package: {layer_zip}")
    return layer_zip

def upload_layer(layer_zip, region='us-east-1'):
    """Upload layer to AWS Lambda"""
    print("☁️ Uploading layer to AWS Lambda...")
    
    lambda_client = boto3.client('lambda', region_name=region)
    
    with open(layer_zip, 'rb') as f:
        layer_content = f.read()
    
    try:
        response = lambda_client.publish_layer_version(
            LayerName='license-scanner-dependencies',
            Description='Dependencies for License Scanner (Pillow, requests)',
            Content={'ZipFile': layer_content},
            CompatibleRuntimes=['python3.9', 'python3.10', 'python3.11'],
            CompatibleArchitectures=['x86_64']
        )
        
        layer_arn = response['LayerVersionArn']
        print(f"✅ Layer uploaded: {layer_arn}")
        return layer_arn
        
    except Exception as e:
        print(f"❌ Error uploading layer: {e}")
        raise

def update_function_with_layer(layer_arn, region='us-east-1'):
    """Update Lambda function to use the layer"""
    print("🔗 Updating Lambda function with layer...")
    
    lambda_client = boto3.client('lambda', region_name=region)
    
    try:
        response = lambda_client.update_function_configuration(
            FunctionName='license-scanner-api',
            Layers=[layer_arn]
        )
        
        print("✅ Function updated with layer")
        return response['FunctionArn']
        
    except Exception as e:
        print(f"❌ Error updating function: {e}")
        raise

def main():
    """Main function"""
    print("🚀 Creating and deploying Lambda layer...")
    print("=" * 50)
    
    try:
        # Step 1: Create layer package
        layer_zip = create_dependencies_layer()
        
        # Step 2: Upload layer to AWS
        layer_arn = upload_layer(layer_zip)
        
        # Step 3: Update function to use layer
        function_arn = update_function_with_layer(layer_arn)
        
        # Clean up
        os.remove(layer_zip)
        
        print("\n" + "=" * 50)
        print("🎉 Layer deployment completed!")
        print(f"📦 Layer ARN: {layer_arn}")
        print(f"🚀 Function ARN: {function_arn}")
        
    except Exception as e:
        print(f"❌ Layer deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
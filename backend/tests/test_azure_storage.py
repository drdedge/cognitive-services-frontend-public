#!/usr/bin/env python3
"""
Test Azure Storage Authentication
=================================

Quick test to verify your Azure Storage authentication is working.
"""

import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# Load environment variables
load_dotenv()

def test_azure_auth():
    """Test Azure Storage authentication with account key."""
    print("=== Testing Azure Storage Authentication ===\n")
    
    # Get credentials from environment
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "cognitive-services")
    
    print("📋 Configuration:")
    print(f"   Account Name: {account_name}")
    print(f"   Account Key: ***{account_key[-10:] if account_key else 'NOT SET'}")
    print(f"   Container: {container_name}")
    
    if not account_name or not account_key:
        print("\n❌ ERROR: Missing required environment variables")
        print("   Please ensure AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY are set")
        return
    
    # Create client
    print("\n🔄 Creating BlobServiceClient...")
    try:
        account_url = f"https://{account_name}.blob.core.windows.net"
        client = BlobServiceClient(account_url=account_url, credential=account_key)
        print("✅ Client created successfully")
    except Exception as e:
        print(f"❌ ERROR creating client: {e}")
        return
    
    # Test connection by listing containers
    print("\n🔄 Testing connection...")
    try:
        containers = []
        for container in client.list_containers():
            containers.append(container['name'])
            if len(containers) >= 5:
                break
        
        print(f"✅ Connection successful! Found {len(containers)} container(s):")
        for container in containers:
            print(f"   - {container}")
    except Exception as e:
        print(f"❌ ERROR listing containers: {e}")
        print("\n💡 This might mean:")
        print("   1. The account key is incorrect")
        print("   2. The storage account doesn't exist")
        print("   3. Network/firewall issues")
        return
    
    # Check specific container
    print(f"\n🔄 Checking container '{container_name}'...")
    try:
        container_client = client.get_container_client(container_name)
        properties = container_client.get_container_properties()
        print(f"✅ Container '{container_name}' exists")
        print(f"   Last modified: {properties.get('last_modified', 'Unknown')}")
    except Exception as e:
        if "ContainerNotFound" in str(e):
            print(f"⚠️  Container '{container_name}' does not exist")
            print("   Creating it now...")
            try:
                container_client.create_container()
                print(f"✅ Container '{container_name}' created successfully")
            except Exception as create_error:
                print(f"❌ ERROR creating container: {create_error}")
        else:
            print(f"❌ ERROR: {e}")
    
    # Test upload
    print("\n🔄 Testing upload capability...")
    try:
        test_blob_name = "_test_auth.txt"
        blob_client = client.get_blob_client(container=container_name, blob=test_blob_name)
        
        test_data = b"This is a test blob to verify authentication works correctly."
        blob_client.upload_blob(test_data, overwrite=True)
        print(f"✅ Successfully uploaded test blob: {test_blob_name}")
        
        # Clean up
        blob_client.delete_blob()
        print("✅ Successfully deleted test blob")
        
    except Exception as e:
        print(f"❌ ERROR testing upload: {e}")
    
    print("\n✅ All tests passed! Your Azure Storage authentication is working correctly.")
    print("\n📝 You can now:")
    print("   1. Use the updated StorageService in your application")
    print("   2. Remove or comment out AZURE_STORAGE_CONNECTION_STRING from .env")
    print("   3. The service will automatically use your account key authentication")

if __name__ == "__main__":
    test_azure_auth()
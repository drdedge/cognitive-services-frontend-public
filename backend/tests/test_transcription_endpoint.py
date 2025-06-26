#!/usr/bin/env python3
"""
Test script to verify transcription endpoint is working.
Run from backend directory: python tests/test_transcription_endpoint.py
"""
import asyncio
import aiohttp
import os
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
AUDIO_FILE_PATH = r"C:\Users\david\Downloads\Monologue.ogg"

async def test_transcription_endpoint():
    """Test the transcription endpoint with a real audio file."""
    
    print(f"Testing transcription endpoint with file: {AUDIO_FILE_PATH}")
    
    # Check if file exists
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"ERROR: File not found: {AUDIO_FILE_PATH}")
        return
    
    file_size = os.path.getsize(AUDIO_FILE_PATH)
    print(f"File size: {file_size / 1024 / 1024:.2f} MB")
    
    # Create form data
    async with aiohttp.ClientSession() as session:
        # First, test if the server is running
        try:
            async with session.get(f"{API_URL}/health") as response:
                if response.status == 200:
                    print("✓ Server is running")
                else:
                    print(f"✗ Server health check failed: {response.status}")
        except aiohttp.ClientError as e:
            print(f"✗ Cannot connect to server at {API_URL}: {e}")
            print("Make sure the backend server is running: python main.py")
            return
        
        # Test languages endpoint first
        print("\nTesting /api/transcription/languages endpoint...")
        try:
            async with session.get(f"{API_URL}/api/transcription/languages") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Languages endpoint working. Found {len(data.get('languages', []))} languages")
                else:
                    print(f"✗ Languages endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
        except Exception as e:
            print(f"✗ Error calling languages endpoint: {e}")
        
        # Test transcribe endpoint
        print(f"\nTesting /api/transcription/transcribe endpoint...")
        
        try:
            # Prepare the file upload
            with open(AUDIO_FILE_PATH, 'rb') as f:
                form_data = aiohttp.FormData()
                form_data.add_field('file', 
                                   f, 
                                   filename=os.path.basename(AUDIO_FILE_PATH),
                                   content_type='audio/ogg')
                form_data.add_field('language', 'en-US')
                form_data.add_field('enable_diarization', 'true')
                form_data.add_field('max_speakers', '20')
                
                # Send the request
                async with session.post(
                    f"{API_URL}/api/transcription/transcribe",
                    data=form_data
                ) as response:
                    print(f"Response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print("✓ Transcription started successfully!")
                        print(f"Job ID: {data.get('job_id')}")
                        print(f"Status: {data.get('status')}")
                        print(f"Message: {data.get('message')}")
                        
                        # Now test the status endpoint
                        job_id = data.get('job_id')
                        if job_id:
                            await asyncio.sleep(2)  # Wait a bit
                            print(f"\nChecking job status...")
                            async with session.get(f"{API_URL}/api/transcription/status/{job_id}") as status_response:
                                if status_response.status == 200:
                                    status_data = await status_response.json()
                                    print(f"Job status: {status_data}")
                                else:
                                    print(f"Status check failed: {status_response.status}")
                    
                    elif response.status == 404:
                        print("✗ Endpoint not found (404)")
                        print("The transcription service is not loaded. Check server logs.")
                        error_text = await response.text()
                        print(f"Error response: {error_text}")
                    
                    elif response.status == 400:
                        print("✗ Bad request (400)")
                        error_data = await response.json()
                        print(f"Error: {error_data}")
                    
                    elif response.status == 500:
                        print("✗ Server error (500)")
                        error_text = await response.text()
                        print(f"Error: {error_text}")
                    
                    else:
                        print(f"✗ Unexpected status: {response.status}")
                        error_text = await response.text()
                        print(f"Response: {error_text}")
                        
        except aiohttp.ClientError as e:
            print(f"✗ Request failed: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

async def test_supported_formats():
    """Test the supported formats endpoint."""
    async with aiohttp.ClientSession() as session:
        print("\nTesting /api/transcription/supported-formats endpoint...")
        try:
            async with session.get(f"{API_URL}/api/transcription/supported-formats") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✓ Supported formats:")
                    for fmt in data.get('formats', []):
                        print(f"  - {fmt['extension']}: {fmt['mime_type']}")
                else:
                    print(f"✗ Supported formats endpoint failed: {response.status}")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("=== Transcription Endpoint Test ===\n")
    
    # Run the async test
    asyncio.run(test_transcription_endpoint())
    asyncio.run(test_supported_formats())
    
    print("\n=== Test Complete ===")
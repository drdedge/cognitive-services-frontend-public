#!/usr/bin/env python3
"""
Test script to verify translation endpoint is working.
Run from backend directory: python tests/test_translation_endpoint.py
"""
import asyncio
import aiohttp
import os
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
# Use the test file in fixtures directory
SCRIPT_DIR = Path(__file__).parent
TEST_FILE_PATH = SCRIPT_DIR / "fixtures" / "test_document.txt"

async def test_translation_endpoints():
    """Test the translation endpoints."""
    
    print(f"Testing translation endpoints at {API_URL}")
    
    async with aiohttp.ClientSession() as session:
        # First, test if the server is running
        try:
            async with session.get(f"{API_URL}/health") as response:
                if response.status == 200:
                    print("✓ Server is running")
                    health_data = await response.json()
                    print(f"  Translation service status: {health_data.get('services', {}).get('translation', 'unknown')}")
                else:
                    print(f"✗ Server health check failed: {response.status}")
        except aiohttp.ClientError as e:
            print(f"✗ Cannot connect to server at {API_URL}: {e}")
            print("Make sure the backend server is running: python main.py")
            return
        
        # Test 1: Get supported languages
        print("\n1. Testing GET /api/translation/languages...")
        try:
            async with session.get(f"{API_URL}/api/translation/languages") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Languages endpoint working")
                    print(f"   ✓ Found {data.get('total', len(data.get('languages', [])))} languages")
                    # Show first 5 languages
                    languages = data.get('languages', [])
                    if languages:
                        print("   Sample languages:")
                        for lang in languages[:5]:
                            print(f"     - {lang['code']}: {lang['name']}")
                elif response.status == 503:
                    error_data = await response.json()
                    print(f"   ✗ Service unavailable: {error_data.get('detail', 'Unknown error')}")
                    print("   Check that Azure Translator credentials are set in .env")
                else:
                    error_text = await response.text()
                    print(f"   ✗ Failed: {error_text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 2: Detect language
        print("\n2. Testing POST /api/translation/detect-language...")
        try:
            test_texts = [
                ("Hello world", "en"),
                ("Bonjour le monde", "fr"),
                ("Hola mundo", "es"),
                ("你好世界", "zh-Hans"),
                ("مرحبا بالعالم", "ar")
            ]
            
            for text, expected_lang in test_texts[:3]:  # Test first 3
                async with session.post(
                    f"{API_URL}/api/translation/detect-language",
                    json={"text": text}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        detected = data.get('language', 'unknown')
                        confidence = data.get('confidence', 0)
                        print(f"   ✓ '{text}' -> {detected} (confidence: {confidence:.2f})")
                        if detected != expected_lang:
                            print(f"     Note: Expected {expected_lang}, got {detected}")
                    else:
                        print(f"   ✗ Failed to detect language for '{text}'")
                        error_text = await response.text()
                        print(f"     Error: {error_text}")
                        break
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 3: Translate text
        print("\n3. Testing POST /api/translation/translate-text...")
        try:
            translations = [
                ("Hello world", "es", "Hola mundo"),
                ("Good morning", "fr", "Bonjour"),
                ("Thank you", "ja", "ありがとう"),
                ("Welcome", "de", "Willkommen")
            ]
            
            for source_text, target_lang, expected in translations[:2]:  # Test first 2
                payload = {
                    "text": source_text,
                    "target_language": target_lang,
                    "source_language": "en"
                }
                
                async with session.post(
                    f"{API_URL}/api/translation/translate-text",
                    json=payload
                ) as response:
                    print(f"   Translating '{source_text}' to {target_lang}...")
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        translated = data.get('translated_text', '')
                        print(f"   ✓ Result: '{translated}'")
                        if expected and translated.lower() != expected.lower():
                            print(f"     Note: Expected '{expected}'")
                    else:
                        error_data = await response.json()
                        print(f"   ✗ Translation failed: {error_data.get('detail', 'Unknown error')}")
                        break
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 4: Batch translation
        print("\n4. Testing POST /api/translation/translate-batch...")
        try:
            batch_payload = {
                "texts": ["Hello", "Good morning", "Thank you"],
                "target_languages": ["es", "fr"],
                "source_language": "en"
            }
            
            async with session.post(
                f"{API_URL}/api/translation/translate-batch",
                json=batch_payload
            ) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Batch translation successful")
                    print(f"   ✓ Processed {data.get('total_processed', 0)} texts")
                    
                    # Show first result
                    translations = data.get('translations', [])
                    if translations:
                        first = translations[0]
                        print(f"   Sample: '{first['original_text']}' ->")
                        for trans in first.get('translations', []):
                            print(f"     {trans['language']}: {trans['text']}")
                else:
                    error_text = await response.text()
                    print(f"   ✗ Batch translation failed: {error_text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 5: Cost estimation
        print("\n5. Testing POST /api/translation/estimate-cost...")
        try:
            cost_payload = {
                "text": "This is a sample text for cost estimation.",
                "target_language": "es"
            }
            
            async with session.post(
                f"{API_URL}/api/translation/estimate-cost",
                json=cost_payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Cost estimation successful")
                    print(f"   Estimated cost: ${data.get('estimated_cost', 0):.2f} {data.get('currency', 'USD')}")
                    print(f"   Character count: {data.get('character_count', 0)}")
                else:
                    print(f"   ✗ Cost estimation failed: {response.status}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 6: Document translation (if file exists)
        if TEST_FILE_PATH.exists():
            print(f"\n6. Testing POST /api/translation/translate-document...")
            try:
                with open(TEST_FILE_PATH, 'rb') as f:
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', 
                                       f, 
                                       filename=os.path.basename(TEST_FILE_PATH),
                                       content_type='text/plain')
                    form_data.add_field('target_language', 'es')
                    form_data.add_field('source_language', 'en')
                    
                    async with session.post(
                        f"{API_URL}/api/translation/translate-document",
                        data=form_data
                    ) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            print(f"   ✓ Document translation started")
                            print(f"   Job ID: {data.get('task_id')}")
                            print(f"   Status: {data.get('status')}")
                            
                            # Check status
                            task_id = data.get('task_id')
                            if task_id:
                                await asyncio.sleep(2)
                                async with session.get(f"{API_URL}/api/translation/status/{task_id}") as status_response:
                                    if status_response.status == 200:
                                        status_data = await status_response.json()
                                        print(f"   Job status: {status_data}")
                        else:
                            error_text = await response.text()
                            print(f"   ✗ Document translation failed: {error_text}")
            except Exception as e:
                print(f"   ✗ Error: {e}")
        else:
            print(f"\n6. Skipping document translation test (file not found: {TEST_FILE_PATH})")

async def test_azure_connection():
    """Test direct Azure Translator connection."""
    print("\n=== Testing Direct Azure Connection ===")
    
    # Load credentials from environment
    from dotenv import load_dotenv
    load_dotenv()
    
    endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
    key = os.getenv("AZURE_TRANSLATOR_KEY")
    region = os.getenv("AZURE_TRANSLATOR_REGION")
    
    print(f"Endpoint: {endpoint}")
    print(f"Region: {region}")
    print(f"Key: {'*' * 10 if key else 'NOT SET'}")
    
    if not key:
        print("✗ Azure Translator key not found in environment")
        return
    
    # Test direct API call
    url = f"{endpoint.rstrip('/')}/translator/text/v3.0/translate"
    params = {
        'api-version': '3.0',
        'to': ['es', 'fr']
    }
    
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
        'Ocp-Apim-Subscription-Region': region
    }
    
    body = [{'text': 'Hello world'}]
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, params=params, headers=headers, json=body) as response:
                print(f"\nDirect API Status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    print("✓ Azure Translator API is working!")
                    print(f"Translations: {json.dumps(result, indent=2)}")
                else:
                    error_text = await response.text()
                    print(f"✗ Azure API error: {error_text}")
        except Exception as e:
            print(f"✗ Connection error: {e}")

if __name__ == "__main__":
    print("=== Translation Service Test ===\n")
    
    # Test Azure connection first
    asyncio.run(test_azure_connection())
    
    # Then test the API endpoints
    print("\n=== Testing API Endpoints ===")
    asyncio.run(test_translation_endpoints())
    
    print("\n=== Test Complete ===")
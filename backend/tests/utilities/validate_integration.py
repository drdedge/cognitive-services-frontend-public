#!/usr/bin/env python3
"""
Integration Validation Script
============================

Validates that the backend API endpoints are properly configured
to match frontend service expectations.
"""

import json
import os
import sys
from pathlib import Path

def validate_file_exists(file_path, description):
    """Validate that a file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False

def validate_endpoint_in_file(file_path, endpoint, description):
    """Validate that an endpoint exists in a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if endpoint in content:
                print(f"✅ {description}: {endpoint}")
                return True
            else:
                print(f"❌ {description}: {endpoint} (not found)")
                return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def validate_websocket_config(main_file):
    """Validate WebSocket configuration."""
    try:
        with open(main_file, 'r') as f:
            content = f.read()
            if 'app.websocket("/ws/{client_id}")' in content:
                print("✅ WebSocket endpoint: Properly configured with client_id parameter")
                return True
            elif 'websocket' in content.lower():
                print("⚠️  WebSocket endpoint: Found but may need configuration check")
                return True
            else:
                print("❌ WebSocket endpoint: Not found")
                return False
    except Exception as e:
        print(f"❌ Error validating WebSocket config: {e}")
        return False

def validate_frontend_services():
    """Validate frontend service files exist."""
    frontend_services = [
        "frontend/src/services/apiClient.js",
        "frontend/src/services/documentIntelligenceService.js", 
        "frontend/src/services/translationService.js",
        "frontend/src/services/transcriptionService.js",
        "frontend/src/services/websocketService.js",
        "frontend/src/services/config.js"
    ]
    
    all_exist = True
    for service in frontend_services:
        if not validate_file_exists(service, f"Frontend service"):
            all_exist = False
    
    return all_exist

def validate_backend_apis():
    """Validate backend API files exist and have required endpoints."""
    backend_apis = [
        ("backend/api/document_intelligence.py", [
            "@router.post(\"/process\"",
            "@router.post(\"/estimate-cost\")",
            "@router.get(\"/status/{task_id}\")",
            "@router.get(\"/results/{task_id}\")",
            "@router.get(\"/supported-types\")",
            "@router.get(\"/analysis-types\")"
        ]),
        ("backend/api/translation.py", [
            "@router.post(\"/translate-text\")",
            "@router.post(\"/estimate-cost\")",
            "@router.get(\"/status/{task_id}\")",
            "@router.get(\"/results/{task_id}\")",
            "@router.get(\"/languages\""
        ]),
        ("backend/api/transcription.py", [
            "@router.post(\"/transcribe\"",
            "@router.post(\"/estimate-cost\")",
            "@router.get(\"/status/{task_id}\")",
            "@router.get(\"/results/{task_id}\")"
        ])
    ]
    
    all_valid = True
    for api_file, endpoints in backend_apis:
        if not validate_file_exists(api_file, "Backend API"):
            all_valid = False
            continue
            
        print(f"\n📋 Checking endpoints in {api_file}:")
        for endpoint in endpoints:
            if not validate_endpoint_in_file(api_file, endpoint, f"  Endpoint"):
                all_valid = False
    
    return all_valid

def validate_websocket_integration():
    """Validate WebSocket integration."""
    print("\n🔌 Validating WebSocket Integration:")
    
    # Check backend WebSocket setup
    backend_valid = True
    if not validate_file_exists("backend/services/websocket_manager.py", "WebSocket manager"):
        backend_valid = False
    
    if not validate_websocket_config("backend/main.py"):
        backend_valid = False
    
    # Check frontend WebSocket service
    frontend_valid = validate_file_exists("frontend/src/services/websocketService.js", "Frontend WebSocket service")
    
    if frontend_valid:
        # Check for key WebSocket methods
        ws_methods = [
            "connect(",
            "subscribe(",
            "sendMessage(",
            "handleMessage("
        ]
        for method in ws_methods:
            validate_endpoint_in_file("frontend/src/services/websocketService.js", method, f"  WebSocket method")
    
    return backend_valid and frontend_valid

def validate_cors_configuration():
    """Validate CORS configuration."""
    print("\n🌐 Validating CORS Configuration:")
    return validate_endpoint_in_file("backend/main.py", "CORSMiddleware", "CORS middleware")

def validate_error_handling():
    """Validate error handling configuration."""
    print("\n🚨 Validating Error Handling:")
    
    backend_error_handling = validate_endpoint_in_file(
        "backend/main.py", 
        "exception_handler", 
        "Backend exception handlers"
    )
    
    frontend_error_handling = validate_endpoint_in_file(
        "frontend/src/services/apiClient.js",
        "interceptors.response.use",
        "Frontend response interceptors"
    )
    
    return backend_error_handling and frontend_error_handling

def validate_configuration_files():
    """Validate configuration files."""
    print("\n⚙️  Validating Configuration Files:")
    
    config_files = [
        ("backend/requirements.txt", "Backend dependencies"),
        ("frontend/package.json", "Frontend dependencies"),
        ("backend/main.py", "Backend main application"),
        ("frontend/src/main.js", "Frontend main application")
    ]
    
    all_exist = True
    for config_file, description in config_files:
        if not validate_file_exists(config_file, description):
            all_exist = False
    
    return all_exist

def main():
    """Run all validation checks."""
    print("🔍 Frontend-Backend Integration Validation")
    print("==========================================\n")
    
    checks = [
        ("Configuration Files", validate_configuration_files),
        ("Frontend Services", validate_frontend_services),
        ("Backend APIs", validate_backend_apis),
        ("WebSocket Integration", validate_websocket_integration),
        ("CORS Configuration", validate_cors_configuration),
        ("Error Handling", validate_error_handling)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * len(check_name))
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All integration validation checks passed!")
        print("\n📋 Next Steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Install frontend deps: cd frontend && npm install")
        print("3. Start backend: cd backend && uvicorn main:app --reload")
        print("4. Start frontend: cd frontend && npm run dev")
        print("5. Test with real Azure credentials")
    else:
        print(f"⚠️  {total - passed} validation checks failed. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
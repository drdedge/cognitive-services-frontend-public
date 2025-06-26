#!/usr/bin/env python3
"""
Test runner for ResultPackager tests.

This script runs all ResultPackager-related tests and provides a summary.
"""
import sys
import subprocess
import warnings
from pathlib import Path

# Suppress Pydantic V2 deprecation warnings for now
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")

def run_tests():
    """Run all ResultPackager tests."""
    print("=" * 70)
    print("Running ResultPackager Tests")
    print("=" * 70)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    
    test_files = [
        "tests/test_result_packager_base.py",
        "tests/test_result_packagers.py", 
        "tests/test_result_packager_integration.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        print(f"\n{'=' * 70}")
        print(f"Running: {test_file}")
        print(f"{'=' * 70}")
        
        # Run pytest with verbose output
        cmd = [
            sys.executable, "-m", "pytest", 
            test_file, 
            "-v", 
            "--tb=short",
            "--no-header",
            "-W", "ignore::DeprecationWarning"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=backend_dir,
            capture_output=False
        )
        
        if result.returncode != 0:
            all_passed = False
            print(f"\n❌ FAILED: {test_file}")
        else:
            print(f"\n✅ PASSED: {test_file}")
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    if all_passed:
        print("✅ All ResultPackager tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

def run_specific_test(test_name):
    """Run a specific test or test class."""
    print(f"Running specific test: {test_name}")
    
    backend_dir = Path(__file__).parent.parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "-k", test_name,
        "-W", "ignore::DeprecationWarning"
    ]
    
    result = subprocess.run(cmd, cwd=backend_dir)
    return result.returncode

def run_with_coverage():
    """Run tests with coverage report."""
    print("Running tests with coverage...")
    
    backend_dir = Path(__file__).parent.parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=services.shared.result_packager",
        "--cov=services.document_intelligence.result_packager",
        "--cov=services.translation.result_packager",
        "--cov=services.transcription.result_packager",
        "--cov-report=term-missing",
        "tests/test_result_packager_base.py",
        "tests/test_result_packagers.py",
        "tests/test_result_packager_integration.py",
        "-W", "ignore::DeprecationWarning"
    ]
    
    result = subprocess.run(cmd, cwd=backend_dir)
    return result.returncode

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run ResultPackager tests")
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Run specific test by name (e.g., 'test_package_document_intelligence_results')"
    )
    
    args = parser.parse_args()
    
    if args.coverage:
        exit_code = run_with_coverage()
    elif args.test:
        exit_code = run_specific_test(args.test)
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
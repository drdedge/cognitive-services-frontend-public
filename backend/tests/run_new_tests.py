#!/usr/bin/env python3
"""
Run tests for the new refactored base classes and utilities.
This script specifically runs tests for the new code we're adding.
"""
import os
import sys
import subprocess
from pathlib import Path


def main():
    """Run tests for new base classes and utilities."""
    
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print("🧪 Running Tests for New Base Classes and Utilities")
    print("=" * 60)
    print()
    
    # Test files for new code
    new_test_files = [
        "tests/test_base_service.py",
        "tests/test_file_processor.py"
    ]
    
    # Build pytest command
    test_args = [
        sys.executable, "-m", "pytest",
        "--verbose",
        "--tb=short",
        "-v",
        "--color=yes",
        "--no-header"
    ]
    
    # Add coverage if requested
    if "--coverage" in sys.argv:
        test_args.extend([
            "--cov=services.base",
            "--cov=services.shared",
            "--cov-report=term-missing"
        ])
    
    # Add test files
    test_args.extend(new_test_files)
    
    print("📋 Running tests for:")
    for test_file in new_test_files:
        print(f"   - {test_file}")
    print()
    
    # Run the tests
    try:
        result = subprocess.run(test_args)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("\n✅ All tests for new base classes passed!")
        print("📝 Next steps:")
        print("   1. Create BaseAPIRouter to consolidate API patterns")
        print("   2. Create ResultPackager for consistent ZIP creation")
        print("   3. Start migrating Document Intelligence service")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)
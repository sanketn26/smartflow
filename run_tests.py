#!/usr/bin/env python3
"""
Simple test runner for SmartFlow development.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite."""
    print("🧪 Running SmartFlow tests...")
    
    # Set test environment
    os.environ["TEST_MODE"] = "true"
    
    # Run tests
    try:
        result = subprocess.run([
            "poetry", "run", "pytest", "tests/", 
            "-v", "--tb=short"
        ], check=True)
        
        print("✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Poetry not found. Please install Poetry first.")
        return False


def main():
    """Main function."""
    if not run_tests():
        sys.exit(1)


if __name__ == "__main__":
    main()

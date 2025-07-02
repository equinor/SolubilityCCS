#!/usr/bin/env python3
"""
Test script to verify that path resolution works correctly from different locations
and that proper error handling is in place.
"""

import os
import sys
import tempfile
from pathlib import Path


def test_path_resolution():
    """Test that path resolution works correctly"""
    print("=== Testing Path Resolution ===")

    # Test 1: From project root
    print("\n1. Testing from project root:")
    try:
        from path_utils import get_database_path, get_project_root

        root = get_project_root()
        print(f"   Project root: {root}")

        comp_path = get_database_path("COMP.csv")
        print(f"   COMP.csv path: {comp_path}")

        properties_path = get_database_path("Properties.csv")
        print(f"   Properties.csv path: {properties_path}")

        print("   ✓ All database files found successfully")

    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Check that files actually exist
    print("\n2. Verifying files exist:")
    try:
        import pandas as pd

        # Test reading COMP.csv
        comp_df = pd.read_csv(comp_path)
        print(f"   COMP.csv: {len(comp_df)} rows loaded")

        # Test reading Properties.csv
        props_df = pd.read_csv(properties_path, sep=";")
        print(f"   Properties.csv: {len(props_df)} rows loaded")

        print("   ✓ All database files readable")

    except Exception as e:
        print(f"   ✗ Error reading files: {e}")


def test_error_handling():
    """Test error handling when files don't exist"""
    print("\n=== Testing Error Handling ===")

    # Test with non-existent file
    print("\n1. Testing with non-existent file:")
    try:
        from path_utils import get_database_path

        get_database_path("nonexistent.csv")
        print("   ✗ Should have raised an error!")
    except FileNotFoundError as e:
        print(f"   ✓ Correctly raised FileNotFoundError: {str(e)[:100]}...")
    except Exception as e:
        print(f"   ? Unexpected error type: {type(e).__name__}: {e}")


def test_imports():
    """Test that all imports work with new path handling"""
    print("\n=== Testing Module Imports ===")

    modules_to_test = [
        "fluid",
        "neqsim_functions",
        "sulfuric_acid_activity",
        "path_utils",
    ]

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✓ {module} imported successfully")
        except Exception as e:
            print(f"   ✗ {module} failed: {e}")


def test_from_different_directory():
    """Test that imports work when running from a different directory"""
    print("\n=== Testing from Different Directory ===")

    # Save current directory
    original_dir = os.getcwd()

    try:
        # Create a temporary directory and change to it
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            print(f"   Changed to: {temp_dir}")

            # Add project directory to Python path
            project_root = str(Path(original_dir))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # Try to import and use the modules
            try:
                from path_utils import get_database_path

                comp_path = get_database_path("COMP.csv")
                print(f"   ✓ Found COMP.csv from different directory: {comp_path}")

            except Exception as e:
                print(f"   ✗ Failed to find database from different directory: {e}")

    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == "__main__":
    print("Path Resolution and Error Handling Test")
    print("=" * 50)

    test_path_resolution()
    test_error_handling()
    test_imports()
    test_from_different_directory()

    print("\n" + "=" * 50)
    print("Test completed!")

#!/usr/bin/env python3
"""
Test script to verify that path resolution works correctly from different locations
and that proper error handling is in place.
"""

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest


def test_path_resolution():
    """Test that path resolution works correctly"""
    from path_utils import get_database_path, get_project_root

    # Test 1: From project root
    root = get_project_root()
    assert root is not None, "Project root should be found"
    assert isinstance(root, Path), "Project root should be a Path object"
    assert root.exists(), "Project root directory should exist"

    comp_path = get_database_path("COMP.csv")
    assert comp_path is not None, "COMP.csv path should be returned"
    assert os.path.exists(comp_path), "COMP.csv file should exist"

    properties_path = get_database_path("Properties.csv")
    assert properties_path is not None, "Properties.csv path should be returned"
    assert os.path.exists(properties_path), "Properties.csv file should exist"


def test_database_files_readable():
    """Test that database files can be read by pandas"""
    from path_utils import get_database_path

    # Test reading COMP.csv
    comp_path = get_database_path("COMP.csv")
    comp_df = pd.read_csv(comp_path)
    assert len(comp_df) > 0, "COMP.csv should contain data"
    assert isinstance(comp_df, pd.DataFrame), "COMP.csv should load as DataFrame"

    # Test reading Properties.csv
    properties_path = get_database_path("Properties.csv")
    props_df = pd.read_csv(properties_path, sep=";")
    assert len(props_df) > 0, "Properties.csv should contain data"
    assert isinstance(props_df, pd.DataFrame), "Properties.csv should load as DataFrame"


def test_error_handling():
    """Test error handling when files don't exist"""
    from path_utils import get_database_path

    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        get_database_path("nonexistent.csv")


def test_module_imports():
    """Test that all imports work with new path handling"""
    modules_to_test = [
        "fluid",
        "neqsim_functions",
        "sulfuric_acid_activity",
        "path_utils",
    ]

    for module in modules_to_test:
        # This will raise ImportError if module cannot be imported
        imported_module = __import__(module)
        assert imported_module is not None, f"{module} should be importable"


def test_from_different_directory():
    """Test that imports work when running from a different directory"""
    # Save current directory
    original_dir = os.getcwd()

    try:
        # Create a temporary directory and change to it
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)

            # Add project directory to Python path
            project_root = str(Path(original_dir))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # Try to import and use the modules
            from path_utils import get_database_path

            comp_path = get_database_path("COMP.csv")
            assert (
                comp_path is not None
            ), "Should find COMP.csv from different directory"
            assert os.path.exists(
                comp_path
            ), "COMP.csv should exist when found from different directory"

    finally:
        # Restore original directory
        os.chdir(original_dir)

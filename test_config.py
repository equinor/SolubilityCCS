# Test configuration for environments without database files
from path_utils import get_database_path_legacy


def get_database_path(filename):
    """Get the path to a database file, with fallbacks for different environments"""
    # Use the new path utilities with backwards compatibility
    return get_database_path_legacy(filename)


def setup_test_environment():
    """Set up test environment with or without database files"""
    comp_path = get_database_path("COMP.csv")
    properties_path = get_database_path("Properties.csv")

    return {
        "comp_csv_available": comp_path is not None,
        "properties_csv_available": properties_path is not None,
        "comp_path": comp_path,
        "properties_path": properties_path,
    }

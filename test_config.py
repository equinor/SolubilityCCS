# Test configuration for environments without database files
import os

def get_database_path(filename):
    """Get the path to a database file, with fallbacks for different environments"""
    
    # Try current directory first (for GitHub Actions)
    current_dir = os.getcwd()
    paths_to_try = [
        os.path.join(current_dir, "Database", filename),
        os.path.join(current_dir, filename),
        os.path.join(os.path.dirname(__file__), "Database", filename),
        os.path.join("..", "Database", filename),  # Parent directory
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    
    return None

def setup_test_environment():
    """Set up test environment with or without database files"""
    comp_path = get_database_path("COMP.csv")
    properties_path = get_database_path("Properties.csv")
    
    return {
        "comp_csv_available": comp_path is not None,
        "properties_csv_available": properties_path is not None,
        "comp_path": comp_path,
        "properties_path": properties_path
    }

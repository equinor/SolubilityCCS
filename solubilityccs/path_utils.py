"""Path utilities for handling relative paths and database file locations.

Provides robust path resolution with proper error handling.
"""

import os
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory by looking for key project files.

    Returns
    -------
    Path
        The project root directory

    Raises
    ------
    FileNotFoundError
        If project root cannot be determined
    """
    # Start from the current file's directory
    current_path = Path(__file__).parent.absolute()

    # Look for project indicators (these files should be in the project root)
    project_indicators = ["pyproject.toml", "requirements.txt", "Makefile", "README.md"]

    # Check current directory and parent directories
    for path in [current_path] + list(current_path.parents):
        if any((path / indicator).exists() for indicator in project_indicators):
            return path

    # If no project root found, raise an error
    raise FileNotFoundError(
        f"Could not determine project root directory. "
        f"Please ensure you are running from within the SolubilityCCS "
        f"project directory. Current working directory: {os.getcwd()}"
    )


def get_database_path(filename):
    """Get the absolute path to a database file using package resources.

    Parameters
    ----------
    filename : str
        The database filename (e.g., 'COMP.csv')

    Returns
    -------
    str
        Absolute path to the database file

    Raises
    ------
    FileNotFoundError
        If the database file cannot be found
    """
    try:
        # First try to find the database file relative to this module
        package_dir = Path(__file__).parent.absolute()
        database_path = package_dir / "Database" / filename

        if database_path.exists():
            return str(database_path)

        # Fallback to project root method for development
        project_root = get_project_root()
        database_path = project_root / "Database" / filename

        if not database_path.exists():
            raise FileNotFoundError(
                f"Database file '{filename}' not found at {database_path}. "
                f"Please ensure the Database directory exists and contains "
                f"the required files."
            )

        return str(database_path)

    except Exception as e:
        raise FileNotFoundError(
            f"Failed to locate database file '{filename}': {str(e)}"
        ) from e


def get_database_directory():
    """Get the absolute path to the Database directory.

    Returns
    -------
    str
        Absolute path to the Database directory

    Raises
    ------
    FileNotFoundError
        If the Database directory cannot be found
    """
    try:
        project_root = get_project_root()
        database_dir = project_root / "Database"

        if not database_dir.exists():
            raise FileNotFoundError(
                f"Database directory not found at {database_dir}. "
                f"Please ensure the Database directory exists in the project root."
            )

        return str(database_dir)

    except Exception as e:
        raise FileNotFoundError(f"Failed to locate Database directory: {str(e)}") from e


def safe_file_read(file_path, error_context=""):
    """Safely check if a file exists and is readable.

    Parameters
    ----------
    file_path : str
        Path to the file
    error_context : str
        Additional context for error messages

    Returns
    -------
    bool
        True if file exists and is readable

    Raises
    ------
    FileNotFoundError
        If file doesn't exist or isn't readable
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Required file not found: {file_path}. {error_context}"
        )

    if not os.access(file_path, os.R_OK):
        raise PermissionError(
            f"Cannot read file: {file_path}. Check file permissions. {error_context}"
        )

    return True


def get_venv_python_path():
    """Get the path to the Python interpreter in the virtual environment.

    Returns
    -------
    str
        Path to the Python interpreter

    Raises
    ------
    FileNotFoundError
        If virtual environment Python cannot be found
    """
    try:
        project_root = get_project_root()
        venv_python = project_root / "venv" / "bin" / "python"

        if not venv_python.exists():
            # Try alternative locations
            alternative_paths = [
                project_root / "venv" / "Scripts" / "python.exe",  # Windows
                Path(sys.executable),  # Current Python interpreter
            ]

            for alt_path in alternative_paths:
                if alt_path.exists():
                    return str(alt_path)

            raise FileNotFoundError(
                f"Virtual environment Python not found. Expected at {venv_python}. "
                f"Please ensure the virtual environment is set up correctly."
            )

        return str(venv_python)

    except Exception as e:
        raise FileNotFoundError(
            f"Failed to locate virtual environment Python: {str(e)}"
        ) from e


# For backwards compatibility, provide the same interface as test_config.py
def get_database_path_legacy(filename):
    """Legacy function for backwards compatibility with test_config.py.

    Returns None if file not found (instead of raising exception).
    """
    try:
        return get_database_path(filename)
    except FileNotFoundError:
        return None

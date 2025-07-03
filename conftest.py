"""
Test configuration for pytest.

This module provides fixtures and configuration for proper test execution,
including JPype/neqsim cleanup to prevent segmentation faults.
"""

import atexit
import warnings

import pytest


def pytest_configure(config):
    """Configure pytest session."""
    # Suppress specific warnings that might occur during testing
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", message=".*JPype.*")


def pytest_unconfigure(config):
    """Clean up after pytest session."""
    try:
        # Try to properly shut down JPype if it's running
        import jpype

        if jpype.isJVMStarted():
            jpype.shutdownJVM()
    except (ImportError, Exception):
        # If JPype is not available or shutdown fails, just continue
        pass


@pytest.fixture(scope="session", autouse=True)
def cleanup_jpype():
    """Ensure proper cleanup of JPype after tests."""
    yield

    # Clean up JPype after all tests
    try:
        import jpype

        if jpype.isJVMStarted():
            jpype.shutdownJVM()
    except (ImportError, Exception):
        # If JPype is not available or shutdown fails, just continue
        pass


# Register cleanup at exit as a backup
def _cleanup_jpype_at_exit():
    """Backup cleanup function registered with atexit."""
    try:
        import jpype

        if jpype.isJVMStarted():
            jpype.shutdownJVM()
    except (ImportError, Exception):
        pass


atexit.register(_cleanup_jpype_at_exit)

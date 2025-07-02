"""Test version utilities."""

import re

import solubilityccs


def test_get_version():
    """Test the get_version utility function."""
    version = solubilityccs.get_version()

    # Version should be a string
    assert isinstance(version, str)

    # Version should match semantic versioning pattern (major.minor.patch)
    # Allow for development versions like "0.1.0-dev" or "0.1.1.dev0+gc850970.d20250702"
    version_pattern = r"^\d+\.\d+\.\d+([.-]\w+(\+\w+(\.\w+)?)?)?$"
    assert re.match(
        version_pattern, version
    ), f"Version '{version}' doesn't match expected pattern"

    # Should match the __version__ attribute
    assert version == solubilityccs.__version__


def test_version_attribute():
    """Test that __version__ is available."""
    version = solubilityccs.__version__
    assert isinstance(version, str)
    assert len(version) > 0

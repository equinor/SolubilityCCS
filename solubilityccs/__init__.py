"""SolubilityCCS - Carbon Capture and Storage Solubility Analysis Package.

A Python package for analyzing solubility and acid formation behavior in
Carbon Capture and Storage (CCS) systems.
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations
    __version__ = "0.1.0-dev"

# Import main modules
try:
    from .fluid import Fluid, Phase
    from .neqsim_functions import (
        get_acid_fugacity_coeff,
        get_water_fugacity_coefficient,
    )
    from .path_utils import get_database_path
    from .sulfuric_acid_activity import calc_activity_water_h2so4

    __all__ = [
        "__version__",
        "Fluid",
        "Phase",
        "get_acid_fugacity_coeff",
        "get_water_fugacity_coefficient",
        "calc_activity_water_h2so4",
        "get_database_path",
    ]
except ImportError as e:
    # Handle import errors gracefully during development
    import warnings

    warnings.warn(f"Some modules could not be imported: {e}", ImportWarning)

    # Still try to import basic utilities that don't depend on neqsim
    try:
        from .path_utils import get_database_path
        from .sulfuric_acid_activity import calc_activity_water_h2so4

        __all__ = ["__version__", "get_database_path", "calc_activity_water_h2so4"]
    except ImportError:
        __all__ = ["__version__"]

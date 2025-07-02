#!/usr/bin/env python3
"""Test runner script for the SolubilityCCS project."""

import os
import subprocess  # nosec B404
import sys


def run_tests():
    """Run the test suite."""
    print("Running SolubilityCCS Test Suite...")
    print("=" * 50)

    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # Python executable - use current interpreter
    python_cmd = sys.executable

    try:
        # Run pytest with coverage
        subprocess.run(  # nosec B603
            [
                python_cmd,
                "-m",
                "pytest",
                "--cov=.",
                "--cov-report=html",
                "--cov-report=term-missing",
                "-v",
            ],
            check=True,
            capture_output=False,
        )

        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("Coverage report generated in htmlcov/index.html")

        return True

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Tests failed!")
        print(f"Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Python or pytest not found!")
        print(f"Current Python executable: {python_cmd}")
        print("Please ensure pytest is installed: pip install pytest pytest-cov")
        return False


def run_quick_tests():
    """Run quick tests without coverage."""
    print("Running Quick Tests...")
    print("=" * 30)

    # Python executable - use current interpreter
    python_cmd = sys.executable

    try:
        subprocess.run(  # nosec B603
            [python_cmd, "-m", "pytest", "-v", "--tb=short"],
            check=True,
            capture_output=False,
        )

        print("\n✅ Quick tests passed!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Quick tests failed! Exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ Python or pytest not found!")
        print(f"Current Python executable: {python_cmd}")
        print("Please ensure pytest is installed: pip install pytest")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = run_quick_tests()
    else:
        success = run_tests()

    sys.exit(0 if success else 1)

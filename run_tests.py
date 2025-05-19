"""
Test runner script for the FirstStreet Backend application.

This script runs all the unit tests in the app/tests directory using pytest.
"""

import pytest
import sys
import os


def main():
    """Run all tests in the app/tests directory."""
    print("Running FirstStreet Backend tests...")

    # Add the current directory to the path so pytest can find the app package
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Run the tests
    args = [
        "app/tests",  # Test directory
        "-v",         # Verbose output
        "--tb=short", # Short traceback format
        "--cov=app",  # Coverage for app directory
        "--cov-report=term",  # Terminal coverage report
        "--cov-report=html:coverage_reports/html",  # HTML coverage report
    ]

    # Add any command line arguments
    args.extend(sys.argv[1:])

    # Run pytest
    exit_code = pytest.main(args)

    # Return the exit code
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

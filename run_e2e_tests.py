"""
Script to run end-to-end tests for the FirstStreet Backend application.

This script runs the end-to-end tests that verify critical user flows through the web UI.
"""

import os
import sys
import pytest

if __name__ == "__main__":
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Set the Flask environment to testing
    os.environ["FLASK_ENV"] = "testing"

    # Run the end-to-end tests
    print("Running end-to-end tests...")
    result = pytest.main([
        "-v", 
        "app/tests/e2e",
        "--cov=app",  # Coverage for app directory
        "--cov-report=term",  # Terminal coverage report
        "--cov-report=html:coverage_reports/e2e_html",  # HTML coverage report
    ])

    # Print a summary of the test results
    if result == 0:
        print("\nAll end-to-end tests passed!")
    else:
        print("\nSome end-to-end tests failed. Please check the output above for details.")

    sys.exit(result)

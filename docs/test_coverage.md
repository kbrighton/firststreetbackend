# Test Coverage Reporting

This document explains how to use the test coverage reporting functionality in the FirstStreet Backend project.

## Overview

Test coverage reporting is a way to measure how much of your code is being tested by your test suite. It helps identify areas of the codebase that lack test coverage, which can be useful for improving the quality and reliability of the code.

The FirstStreet Backend project uses [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/), a plugin for pytest that integrates with the [coverage.py](https://coverage.readthedocs.io/en/latest/) library to provide test coverage reporting.

## Running Tests with Coverage Reporting

### Unit Tests

To run unit tests with coverage reporting, use the `run_tests.py` script:

```bash
python run_tests.py
```

This will:
1. Run all unit tests in the `app/tests` directory
2. Generate a coverage report for the `app` directory
3. Display a summary of the coverage report in the terminal
4. Generate an HTML coverage report in the `coverage_reports/html` directory

### End-to-End Tests

To run end-to-end tests with coverage reporting, use the `run_e2e_tests.py` script:

```bash
python run_e2e_tests.py
```

This will:
1. Run all end-to-end tests in the `app/tests/e2e` directory
2. Generate a coverage report for the `app` directory
3. Display a summary of the coverage report in the terminal
4. Generate an HTML coverage report in the `coverage_reports/e2e_html` directory

## Viewing Coverage Reports

### Terminal Report

After running tests with coverage reporting, a summary of the coverage report will be displayed in the terminal. This includes:
- The percentage of code covered by tests
- The number of statements, missing statements, and excluded statements
- A list of files with their individual coverage percentages

### HTML Report

For a more detailed view of the coverage report, you can open the HTML report in a web browser:

1. For unit tests: Open `coverage_reports/html/index.html`
2. For end-to-end tests: Open `coverage_reports/e2e_html/index.html`

The HTML report provides:
- An overview of the coverage for the entire project
- Coverage details for each file
- Line-by-line highlighting of covered and uncovered code

## Configuration

The coverage reporting is configured in the `pytest.ini` file in the project root directory. This file specifies:
- Which directories to include in the coverage report
- Which files to exclude from the coverage report
- Which lines to exclude from the coverage report (e.g., `__repr__` methods, `NotImplementedError`, etc.)

If you need to modify the coverage configuration, edit the `pytest.ini` file.

## Best Practices

- Aim for high test coverage, but remember that 100% coverage doesn't guarantee bug-free code
- Focus on covering critical and complex parts of the codebase
- Use the coverage report to identify areas that need more tests
- Regularly run tests with coverage reporting to track progress
# Continuous Integration Setup

This document describes the continuous integration (CI) setup for the FirstStreet Backend application.

## Overview

The CI pipeline is implemented using GitHub Actions and automatically runs whenever code is pushed to the main/master branch or when a pull request is created against these branches. The pipeline performs the following tasks:

1. Sets up a Python environment
2. Installs project dependencies
3. Runs unit tests
4. Runs end-to-end tests
5. Uploads test coverage reports as artifacts

## Configuration

The CI configuration is defined in the `.github/workflows/ci.yml` file. It uses the following key components:

### Environment

- **Python**: Version 3.9
- **Database**: PostgreSQL 13
- **Environment Variables**:
  - `FLASK_ENV=testing`: Ensures the application runs in testing mode
  - `TEST_DATABASE_URL`: Points to the PostgreSQL database
  - `SECRET_KEY`: A test secret key for the application

### Test Execution

The CI pipeline runs two types of tests:

1. **Unit Tests**: Using `run_tests.py`, which runs all tests in the `app/tests` directory (excluding end-to-end tests)
2. **End-to-End Tests**: Using `run_e2e_tests.py`, which runs tests in the `app/tests/e2e` directory

Both test runs generate coverage reports that are uploaded as artifacts.

## Viewing Test Results

Test results are displayed directly in the GitHub Actions UI. If any tests fail, the pipeline will fail, and you can see the specific test failures in the logs.

Coverage reports are uploaded as artifacts and can be downloaded from the GitHub Actions run page.

## Maintenance

### Adding New Tests

New tests will automatically be included in the CI pipeline as long as they follow the naming conventions:

- Test files should be named `test_*.py`
- Test functions should be named `test_*`

### Modifying the CI Configuration

If you need to modify the CI configuration:

1. Edit the `.github/workflows/ci.yml` file
2. Commit and push your changes
3. The updated configuration will be used for subsequent CI runs

### Common Modifications

- **Adding Environment Variables**: Add them to the `env` section of the relevant test step
- **Changing Python Version**: Update the `python-version` parameter in the "Set up Python" step
- **Adding New Test Steps**: Add new steps following the existing pattern

## Troubleshooting

If the CI pipeline fails, check the following:

1. **Test Failures**: Look at the test output to see which tests failed and why
2. **Environment Issues**: Ensure all required environment variables are set correctly
3. **Dependency Problems**: Check if all dependencies are installed correctly

For persistent issues, you may need to run the tests locally with the same configuration to debug.
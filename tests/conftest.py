"""
Test configuration and fixtures for the FastAPI application.

This module provides shared fixtures for testing the Mergington High School API,
including a test client and activity state management.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a FastAPI test client for making requests to the application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset the in-memory activities database to its initial state before and after each test.
    
    This fixture ensures test isolation by saving the original activities state before
    the test runs and restoring it afterwards, preventing test interdependencies.
    """
    # Save the original state
    original_activities = deepcopy(activities)
    
    yield  # Run the test
    
    # Restore the original state after the test
    activities.clear()
    activities.update(original_activities)

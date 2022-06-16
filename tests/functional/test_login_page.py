import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from app import create_app

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!

def test_login_page_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Welcome to DanioDB!" not in response.data
    assert b"New User?" in response.data
    assert b"Forgot Your Password?" in response.data
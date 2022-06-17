import pytest
import os
import sys

from tests.testing_config import Testing_config

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from app import create_app


@pytest.fixture(scope='module')
def client():
    """
    This is used to help with testing in all the view functions of the project
    This method uses the normal configurartions files
    """
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
def test_client():
    """
    This is used to help with testing in all the view functions of the project
    This method uses the testing configurartions files
    """
    flask_app = create_app(config_Class=Testing_config)

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!

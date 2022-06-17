import datetime
import pytest
import os
import sys

from tests.testing_config import Testing_config

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from app import create_app
from app.models import User, Fish


#TO RUN ALL TESTS USE THE 'python -m pytest' COMMAND

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


@pytest.fixture(scope='module')
def new_user():
    """
    THIS IS USED TO CREATE USERS FOR OTHER TESTS USING PYTEST
    """
    user = User(first_name="John", last_name = "Smith" ,email = "testing@bath.ac.uk")
    user.set_password("examplePassword123")
    return user




@pytest.fixture(scope='module')
def new_fish():
    """
    THIS IS USED TO CREATE A FISH FOR OTHER TESTS USING PYTEST
    """
    fish = Fish(
        fish_id = "1a2b4c",
        birthday = datetime.datetime(2020, 5, 17),
        date_of_arrival = datetime.datetime(2021, 5, 17),
        stock = "ABC123",
        project_license = "QWERTY",
        status = "Alive",
        allele = "aa",
        protocol = 1,
        comments = "Its a fish..."
        ) 

    return fish
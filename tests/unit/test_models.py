import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from app.models import User

#TO RUN ALL TESTS USE THE 'python -m pytest' COMMAND

@pytest.fixture(scope='module')
def new_user():
    """
    THIS IS USED TO CREATE USERS FOR OTHER TESTS USING PYTEST
    """
    user = User(first_name="John", last_name = "Smith" ,email = "testing@bath.ac.uk")
    user.set_password("examplePassword123")
    return user



def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, names and verification fields are defined correctly
    """
   
    #check the email is stored correctly
    assert new_user.email == "testing@bath.ac.uk"

    #Check names
    assert new_user.first_name == "John"
    assert new_user.last_name == "Smith"

    #make sure the hash is not stored as the plaintext
    assert new_user.password_hash != "examplePassword123"

    assert new_user.check_password("examplePassword123")
    assert not new_user.check_password("incorrectPassword123")

    #make sure they are not yet verified
    assert not new_user.is_verified
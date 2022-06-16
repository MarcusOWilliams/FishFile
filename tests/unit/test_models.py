import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
from app.models import User


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, names and verification fields are defined correctly
    """
   

    #the users for tests are never commited to the actual databes, so don't need to worry about secure passwords, just for testing purposes
    user = User(first_name="John", last_name = "Smith" ,email = "testing@bath.ac.uk")
    user.set_password("examplePassword123")

    #check the email is stored correctly
    assert user.email == "testing@bath.ac.uk"

    #Check names
    assert user.first_name == "John"
    assert user.last_name == "Smith"

    #make sure the hash is not stored as the plaintext
    assert user.password_hash != "examplePassword123"

    assert user.check_password("examplePassword123")
    assert not user.check_password("incorrectPassword123")

    #make sure they are not yet verified
    assert not user.is_verified


test_new_user()
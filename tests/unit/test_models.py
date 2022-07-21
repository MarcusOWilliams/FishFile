from datetime import datetime

from tests.conftest import new_notification


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



def test_new_fish(new_fish):
    """
    GIVEN a Fish model
    WHEN a new Fish is created
    THEN check the properties are defined correctly
    """
    assert new_fish.fish_id == "1a2b4c"
    assert new_fish.birthday == datetime(2016,4,30,3,20,6)
    assert new_fish.date_of_arrival == datetime(2016,4,30,3,20,6)
    assert new_fish.stock == "ABC123"
    assert new_fish.transgenes == None
    assert new_fish.comments == "Its a fish..."

    

def test_new_change(new_change):
    """
    GIVEN a Change model
    WHEN a new Change is created
    THEN check the properties are defined correctly
    """
    assert new_change.user_id == 1
    assert new_change.fish_id == 1
    assert new_change.action == "test"
    assert new_change.contents == "this is a test"

def test_new_notification(new_notification):
    """
    GIVEN a Notification model
    WHEN a new Notification is created
    THEN check the properties are defined correctly
    """
    assert new_notification.user_id == 1
    assert new_notification.category == "test"
    assert new_notification.contents == "this is a test"

def test_new_setting(new_setting):
    """
    GIVEN a Setting model
    WHEN a new Setting is created
    THEN check the properties are defined correctly
    """
    assert new_setting.user_id == 1
    assert new_setting.emails == False
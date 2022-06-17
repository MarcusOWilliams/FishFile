
def test_login_page(new_user, test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid
    """

    new_user.login
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Welcome to DanioDB!" not in response.data
    assert b"New User?" in response.data
    assert b"Forgot Your Password?" in response.data

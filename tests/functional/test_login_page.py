
def test_login_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"Welcome to FishFile!" not in response.data
    assert b"New User?" in response.data
    assert b"Forgot Your Password?" in response.data

def test_incorrects_login_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signin' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/signin')
    assert response.status_code == 404

def test_login_page_post(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is POSTED to (POST)
    THEN check that the response is valid
    """
    response = client.post('/login')
    assert response.status_code == 200
    assert b"This field is required" in response.data

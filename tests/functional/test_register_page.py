def test_register_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data
    assert b"Welcome to DanioDB!" not in response.data
    assert b"Already have an account?" in response.data

def test_incorrects_register_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/signup')
    assert response.status_code == 404

def test_register_page_post(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is POSTED to (POST)
    THEN check that the response is valid
    """
    response = client.post('/register')
    assert response.status_code == 200
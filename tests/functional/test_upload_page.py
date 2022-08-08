
def test_upload_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/upload')
    assert response.status_code == 200
    assert b"New" in response.data
    assert b"Fish ID" not in response.data
    assert b"Submit" in response.data

def test_incorrect_upload_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/uploadfish' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/uploadfish')
    assert response.status_code == 404

def test_upload_page_post(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload' page is POSTED to (POST)
    THEN check that the response is valid
    """
    response = client.post('/newfish')
    assert response.status_code == 200
    assert b"New" in response.data

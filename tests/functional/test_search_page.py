
def test_search_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/search' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/search')
    assert response.status_code == 200
    assert b"Results" in response.data
    assert b"Fish ID" not in response.data
    assert b"Submit" in response.data

def test_incorrect_searh_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/search' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/results')
    assert response.status_code == 404

def test_upload_page_post(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/search' page is POSTED to (POST)
    THEN check that the response is valid
    """
    response = client.post('/search')
    assert response.status_code == 200
    assert b"Results" in response.data

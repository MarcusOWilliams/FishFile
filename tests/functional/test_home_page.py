
from flask import url_for,request

def test_home_page(test_client_normal):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) 
    AND the user is not logged in
    THEN check that the response is a redirect
    """

    #check for a redirect response
    response = test_client_normal.get('/')
    assert response.status_code == 302

    #check the redirect goes to the login page
    response = test_client_normal.get('/', follow_redirects=True)
    assert request.path == url_for('auth.login')

def test_home_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) 
    AND the user authentication is bypassed
    THEN check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200

    assert b"Hi," in response.data
    assert b"incorrect" not in response.data

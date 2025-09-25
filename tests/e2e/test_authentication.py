import pytest

from flask import session

def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200
    assert b'WELCOME TO OUR RECIPE PORTAL!' in response.data

def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid user name and password.
    response = client.post(
        '/authentication/register',
        data={'user_name': 'gmichael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == '/authentication/login'

def test_register_with_invalid_input(client, user_name, password, message):
    # Check that attempting to register with invalid combinations of user name and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'user_name': "tester", 'password': "aasdf"}
    )

    # check for error message when register inputs are invalid
    response = client.post(
        '/authentication/register',
        data = {'username': user_name, 'password': password}
    )

    assert message in response.data

def test_login(client, auth):
    # Register user first
    client.post('/authentication/register', data={
        'user_name': 'tester', 'password': 'Password123!'
    })
    # Then login
    response = client.post('/authentication/login', data={
        'user_name': 'tester', 'password': 'Password123!'
    })
    assert response.headers['Location'] == '/'


@pytest.mark.parametrize(('user_name', 'password', 'message'), (
        ('', '', b'Your user name is required'),
        ('cj', '', b'Your user name is too short'),
        ('test', '', b'Your password is required'),
        ('test', 'test', b'Your password must be at least 8 characters, and contain an upper case letter,\
            a lower case letter and a digit'),
        ('fmercury', 'Test#6^0', b'Your username is already taken - please supply another'),
))

def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session
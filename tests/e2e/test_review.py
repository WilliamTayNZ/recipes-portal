import pytest

from flask import session

def test_login_required_to_post_review(client):
    response = client.post('/recipe/38/review')
    assert response.headers['Location'] == '/authentication/login'


def test_review(client, auth):
    # register and login user
    client.post(
        '/authentication/register',
        data={'username': 'fruitspunchsamurai', 'password': 'z8K*d&a#'}
    )
    auth.login()

    response = client.post('/recipe/38/review',
                           data={'rating': 5, 'comment':'i love this recipe'})
    assert response.headers['Location'] == '/recipe/38?next=home'

@pytest.mark.parametrize(('comment', 'rating', 'messages'), (
    ('', 5, b'This field is required.'),
    ('i love this recipe', None, b'This field is required.'),
    ('', None, b'This field is required.'),
    ('hi', 5, b'Your review is too short'),
    ('hi', None, (b'Your review is too short', b'This field is required.')),
    ('fuck this recipe', 5, b'Field must not contain profanity')
))
def test_review_with_invalid_input(client, auth, comment, rating, messages):
    # register and login user
    client.post(
        '/authentication/register',
        data={'username': 'fruitspunchsamurai', 'password': 'z8K*d&a#'}
    )
    auth.login()

    # attempt to post a review
    response = client.post('/recipe/38/review',
                           data={'rating': rating, 'comment': comment})
    # check that supplying invalid review input generates appropriate error messages
    for message in messages:
        assert message in response.data

def test_recipe_with_review(client, auth):
    # register and login user
    client.post(
        '/authentication/register',
        data={'username': 'fruitspunchsamurai', 'password': 'z8K*d&a#'}
    )
    auth.login()

    # post reviews
    client.post('/recipe/38/review',
                data={'rating': 2, 'comment': 'tasted bad'})
    client.post('/recipe/38/review',
                data={'rating': 4, 'comment': 'pretty good'})

    # check comments are visible
    response = client.get('/recipe/38')
    assert b'tasted bad' in response.data
    assert b'pretty good' in response.data

    # check rating
    assert b'3.0' in response.data
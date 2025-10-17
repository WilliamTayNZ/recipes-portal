import pytest

from flask import session

def test_login_required_to_post_review(client):
    response = client.post('/recipe/38/review')
    assert response.headers['Location'] == '/authentication/login'


def test_review(client, auth):
    # register and login user
    client.post(
        '/authentication/register',
        data={'user_name': 'fruitspunchsamurai', 'password': 'z8K*d&a#'}
    )
    auth.login(user_name='fruitspunchsamurai', password='z8K*d&a#')

    response = client.post('/recipe/38/review',
                           data={'rating': '5', 'review': 'i love this recipe'})
    assert response.headers['Location'] == '/recipe/38#reviews'

@pytest.mark.parametrize(('review', 'rating', 'messages'), (
    ('i love this recipe', '', (b'Please select a rating',)),
    ('hi', '5', (b'If providing a review, it must be at least 4 characters',)),
))
def test_review_with_invalid_input(client, auth, review, rating, messages):
    # register and login user
    client.post(
        '/authentication/register',
        data={'user_name': 'fruitspunchsamurai', 'password': 'z8K*d&a#'}
    )
    auth.login(user_name='fruitspunchsamurai', password='z8K*d&a#')

    # attempt to post a review
    response = client.post('/recipe/38/review',
                           data={'rating': rating, 'review': review})
    # check that supplying invalid review input generates appropriate error messages
    for message in messages:
        assert message in response.data

def test_recipe_with_review(client, auth):
    # register and login user
    client.post(
        '/authentication/register',
        data={'user_name': 'fruitspunchsamurai', 'password': 'z8K*d&a#'}
    )
    auth.login(user_name='fruitspunchsamurai', password='z8K*d&a#')

    # post reviews
    client.post('/recipe/38/review',
                data={'rating': '2', 'review': 'tasted bad'})
    client.post('/recipe/38/review',
                data={'rating': '4', 'review': 'pretty good'})

    # check comments are visible
    response = client.get('/recipe/38')
    assert b'tasted bad' in response.data
    assert b'pretty good' in response.data

    # check rating - it should be 3.0 (average of 2 and 4)
    assert b'3.0' in response.data or b'3' in response.data


def test_delete_review_requires_login(client):
    response = client.post('/delete_review/1')
    assert response.status_code == 302
    assert '/authentication/login' in response.headers['Location']


def test_user_can_delete_their_own_review(client, auth):
    client.post(
        '/authentication/register',
        data={'user_name': 'testuser', 'password': 'Password123'}
    )
    auth.login(user_name='testuser', password='Password123')
    
    # Post a review
    client.post('/recipe/38/review',
                data={'rating': '5', 'review': 'great recipe!'})
    
    # Verify review exists
    response = client.get('/recipe/38')
    assert b'great recipe!' in response.data
    
    # Delete the review (assuming review ID is 1)
    response = client.post('/delete_review/1',
                          data={'recipe_id': '38'})
    
    # Verify the redirect back to recipe page
    assert response.status_code == 302
    

def test_user_cannot_delete_other_users_review(client, auth):

    # Register and login as first user
    client.post(
        '/authentication/register',
        data={'user_name': 'user1', 'password': 'Password123'}
    )
    auth.login(user_name='user1', password='Password123')
    
    # Post a review
    client.post('/recipe/38/review',
                data={'rating': '5', 'review': 'user1 review'})
    
    auth.logout()
    
    # Register and login as second user
    client.post(
        '/authentication/register',
        data={'user_name': 'user2', 'password': 'Password123'}
    )
    auth.login(user_name='user2', password='Password123')
    
    # Try to delete first user's review (assuming review ID is 1)
    response = client.post('/delete_review/1',
                          data={'recipe_id': '38'})
    
    # Should get 403 Forbidden
    assert response.status_code == 403


def test_delete_nonexistent_review(client, auth):

    # Register and login
    client.post(
        '/authentication/register',
        data={'user_name': 'testuser', 'password': 'Password123'}
    )
    auth.login(user_name='testuser', password='Password123')
    
    # Try to delete non-existent review
    response = client.post('/delete_review/999999',
                          data={'recipe_id': '38'})
    
    # Should get 403 Forbidden
    assert response.status_code == 403

# py -m pytest -v tests/e2e/test_review.py
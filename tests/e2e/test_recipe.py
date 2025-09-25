import pytest
from flask import session

def test_login_required_to_review(client, auth):
    # Try to post a review without logging in
    response = client.post(
        '/recipe/38/review',
        data={'rating': '5', 'review': 'Great recipe!', 'recipe_id': '38'}
    )
    # Should be redirected to login page
    assert response.headers['Location'].startswith('/authentication/login')

def test_review_can_be_added(client, auth):
    # Login first
    auth.login()
    
    # Get the form first to get any CSRF token
    response = client.get('/recipe/38')
    assert response.status_code == 200
    
    # Submit a valid review
    response = client.post(
        '/recipe/38/review',
        data={
            'rating': '4',
            'review': 'This is a test review',
            'recipe_id': '38'
        },
        follow_redirects=True
    )
    
    # Check that the review appears on the recipe page
    assert b'This is a test review' in response.data
    assert b'thorke' in response.data  # Default test user from auth fixture

def test_review_changes_average_rating(client, auth):
    # Login
    auth.login()
    
    # Get initial recipe page to check rating
    response = client.get('/recipe/38')
    initial_content = response.data.decode('utf-8')
    
    # Submit a review with rating 5
    response = client.post(
        '/recipe/38/review',
        data={
            'rating': '5',
            'review': 'Excellent recipe!',
            'recipe_id': '38'
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Get the recipe page again to check the updated rating
    response = client.get('/recipe/38')
    new_content = response.data.decode('utf-8')
    
    # The new average rating should be different from the initial one
    assert initial_content != new_content
    assert b'5.0/5' in response.data or b'5/5' in response.data

def test_invalid_review_submission(client, auth):
    # Login
    auth.login()
    
    # Test cases for invalid reviews
    test_cases = [
        # Empty rating
        {
            'review': 'Great recipe!', 
            'recipe_id': '38',
            'expected_message': b'Please select a rating'
        },
        # Review too short
        {
            'rating': '4',
            'review': 'Bad',
            'recipe_id': '38',
            'expected_message': b'If providing a review, it must be at least 4 characters'
        },
        # Profanity in review
        {
            'rating': '1',
            'review': 'This contains profanity',
            'recipe_id': '38',
            'expected_message': b'Your review must not contain profanity'
        }
    ]
    
    for test_case in test_cases:
        response = client.post(
            '/recipe/38/review',
            data=test_case,
            follow_redirects=True
        )
        # Check for expected error message
        assert test_case['expected_message'] in response.data

def test_recipe_page_includes_reviews(client, auth):
    # First add a review as a logged-in user
    auth.login()
    test_review = "This is a unique test review"
    
    response = client.post(
        '/recipe/38/review',
        data={
            'rating': '4',
            'review': test_review,
            'recipe_id': '38'
        },
        follow_redirects=True
    )
    auth.logout()
    
    # Now check the recipe page as an anonymous user
    response = client.get('/recipe/38')
    
    # Verify review section exists and contains our test review
    assert b'Reviews' in response.data
    assert test_review.encode() in response.data
    assert b'thorke' in response.data  # Default test user from auth fixture
    assert b'4' in response.data  # Rating should be visible
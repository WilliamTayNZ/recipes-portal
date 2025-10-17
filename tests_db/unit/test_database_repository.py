import pytest
from datetime import datetime

from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review

def make_repo(session_factory) -> SqlAlchemyRepository:
    return SqlAlchemyRepository(session_factory)



# Add review test 
def test_repo_can_add_a_review(session_factory):
    repo = make_repo(session_factory)

    user = repo.get_user('william')
    recipe = repo.get_recipe_by_id(38)
    
    # Count reviews before adding
    initial_review_count = len(recipe.reviews)

    review = Review(69696969, user, recipe, 5, "Dancer is the GOAT")
    repo.add_review(review)

    # Reload the recipe from database to get updated reviews
    updated_recipe = repo.get_recipe_by_id(38)
    
    # Check that review was added
    assert len(updated_recipe.reviews) == initial_review_count + 1
    
    # Verify the review details
    added_review = updated_recipe.reviews[-1]  # Get the last added review
    assert added_review.rating == 5
    assert added_review.review_text == "Dancer is the GOAT"
    assert added_review.user.username == 'william'
    assert added_review.recipe.id == 38


# Review deletion tests
def test_repo_can_delete_a_review(session_factory):
    repo = make_repo(session_factory)
    
    user = repo.get_user('william')
    recipe = repo.get_recipe_by_id(38)
    
    # Add a review
    review = Review(12345, user, recipe, 4, "Great recipe!")
    repo.add_review(review)
    
    # Reload recipe to get the review
    updated_recipe = repo.get_recipe_by_id(38)
    initial_review_count = len(updated_recipe.reviews)
    
    # Find the review we just added
    added_review = [r for r in updated_recipe.reviews if r.review_text == "Great recipe!"][0]
    review_id = added_review.id
    
    # Delete the review
    success = repo.delete_review(review_id, 'william')
    assert success is True
    
    # Reload recipe and verify review was deleted
    updated_recipe = repo.get_recipe_by_id(38)
    assert len(updated_recipe.reviews) == initial_review_count - 1
    
    # Verify the specific review is gone
    remaining_reviews = [r for r in updated_recipe.reviews if r.review_text == "Great recipe!"]
    assert len(remaining_reviews) == 0


def test_repo_cannot_delete_another_users_review(session_factory):
    repo = make_repo(session_factory)
    
    user = repo.get_user('william')
    recipe = repo.get_recipe_by_id(38)
    
    # Add a review as william
    review = Review(54321, user, recipe, 5, "Amazing dish!")
    repo.add_review(review)
    
    # Reload recipe to get the review
    updated_recipe = repo.get_recipe_by_id(38)
    added_review = [r for r in updated_recipe.reviews if r.review_text == "Amazing dish!"][0]
    review_id = added_review.id
    
    # Try to delete as a different user
    success = repo.delete_review(review_id, 'fmercury')
    assert success is False
    
    # Verify review still exists
    updated_recipe = repo.get_recipe_by_id(38)
    remaining_reviews = [r for r in updated_recipe.reviews if r.review_text == "Amazing dish!"]
    assert len(remaining_reviews) == 1


def test_repo_delete_nonexistent_review_returns_false(session_factory):
    repo = make_repo(session_factory)
    
    # Try to delete a review that doesn't exist
    success = repo.delete_review(999999, 'william')
    assert success is False


def test_review_updates_recipe_rating(session_factory):
    repo = make_repo(session_factory)
    
    user1 = repo.get_user('william')
    user2 = repo.get_user('fmercury')
    recipe = repo.get_recipe_by_id(38)
    
    # Add multiple reviews
    review1 = Review(11111, user1, recipe, 4, "Good!")
    review2 = Review(22222, user2, recipe, 5, "Excellent!")
    
    repo.add_review(review1)
    repo.add_review(review2)
    
    # Reload recipe and check rating
    updated_recipe = repo.get_recipe_by_id(38)
    
    # Rating should be average of all reviews
    expected_rating = round(sum(r.rating for r in updated_recipe.reviews) / len(updated_recipe.reviews), 1)
    assert updated_recipe.rating == expected_rating


def test_user_reviews_are_tracked(session_factory):
    repo = make_repo(session_factory)
    
    user = repo.get_user('william')
    recipe = repo.get_recipe_by_id(38)
    
    # Count user's initial reviews
    initial_review_count = len(user.reviews)
    
    # Add a review
    review = Review(77777, user, recipe, 5, "Perfect!")
    repo.add_review(review)
    
    # Reload user and verify review is tracked
    updated_user = repo.get_user('william')
    assert len(updated_user.reviews) == initial_review_count + 1



# Add and retrieve users

def test_repo_can_add_user(session_factory):
    repo = make_repo(session_factory)

    user = User('Dave', 'EasyPassword123')
    repo.add_user(user)

    user2 = repo.get_user('Dave')

    assert user2 == user


def test_repo_can_retrieve_a_user(session_factory):
    repo = make_repo(session_factory)

    user = repo.get_user('fmercury')

    assert user.username == 'fmercury'
    assert user.check_password('mvNNbc1eLA$i')

def test_repo_does_not_retrieve_a_non_existent_user(session_factory):
    repo = make_repo(session_factory)
    user = repo.get_user('thisisanonexistentuserwhichwillneverbemade123')
    assert user is None


# py -m pytest -v tests_db/unit/test_database_repository.py
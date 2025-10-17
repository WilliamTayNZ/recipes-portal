import pytest
from datetime import datetime, timedelta

from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review


def make_repo(session_factory) -> SqlAlchemyRepository:
    return SqlAlchemyRepository(session_factory)

# User tests
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


# Recipe tests
def test_add_and_get_recipe(session_factory):
    """Test adding and retrieving a recipe"""
    repo = make_repo(session_factory)

    # Use a very high ID to avoid conflicts with populated data
    test_recipe_id = 999999
    author = Author(test_recipe_id, "Test Author")
    category = Category("Test Category")

    recipe = Recipe(
        test_recipe_id,
        "Test Recipe",
        author,
        cook_time=30,
        preparation_time=15,
        created_date=datetime(2025, 1, 1),
        description="Test Description",
        category=category,
        rating=4.5,
        servings="2",
        recipe_yield="1 batch",
        ingredients=["flour", "eggs"],
        ingredient_quantities=["1 cup", "2"],
        instructions=["Mix ingredients", "Bake at 350F"],
        images=["http://example.com/image.jpg"]
    )

    repo.add_recipe(recipe)

    retrieved = repo.get_recipe_by_id(test_recipe_id)
    assert retrieved is not None
    assert retrieved.name == "Test Recipe"
    assert retrieved.author.name == "Test Author"
    assert retrieved.category.name == "Test Category"

def test_get_number_of_recipe(session_factory):
    """Test counting recipes"""
    repo = make_repo(session_factory)
    count = repo.get_number_of_recipe()

    # Should have recipes from populated data
    assert count > 0


def test_get_recipes(session_factory):
    """Test getting all recipes"""
    repo = make_repo(session_factory)
    recipes = repo.get_recipes()

    # Should have recipes from populated data
    assert len(recipes) > 0


def test_get_recipe_by_id(session_factory):
    """Test getting a recipe by ID"""
    repo = make_repo(session_factory)

    # Get first recipe to test with
    first_recipe = repo.get_first_recipe()
    assert first_recipe is not None

    # Get it by ID
    retrieved = repo.get_recipe_by_id(first_recipe.id)
    assert retrieved is not None
    assert retrieved.id == first_recipe.id


def test_get_recipes_paginated(session_factory):
    """Test paginated recipe retrieval"""
    repo = make_repo(session_factory)

    page1 = repo.get_recipes_paginated(page=1, per_page=3)
    assert len(page1) <= 3

    page2 = repo.get_recipes_paginated(page=2, per_page=3)
    # Second page might be empty or have recipes
    assert isinstance(page2, list)

# Review tests
def test_repo_can_add_a_review(session_factory):
    repo = make_repo(session_factory)

    user = repo.get_user('william')
    recipe = repo.get_recipe_by_id(38)
    
    # Count reviews before adding
    initial_review_count = len(recipe.reviews)

    review = Review(user, recipe, 5, "Dancer is the GOAT")
    repo.add_review(review)

    # Reload the recipe from database to get updated reviews
    updated_recipe = repo.get_recipe_by_id(38)
    
    # Check that review was added
    assert len(updated_recipe.reviews) == initial_review_count + 1
    
    # Verify the review details
    added_review = updated_recipe.reviews[-1]  # Get the last added review
    assert added_review.id is not None  # ID should be auto-generated
    assert added_review.rating == 5
    assert added_review.review_text == "Dancer is the GOAT"
    assert added_review.user.username == 'william'
    assert added_review.recipe.id == 38

def test_repo_can_delete_a_review(session_factory):
    repo = make_repo(session_factory)
    
    user = repo.get_user('william')
    recipe = repo.get_recipe_by_id(38)
    
    # Add a review
    review = Review(user, recipe, 4, "Great recipe!")
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
    review = Review(user, recipe, 5, "Amazing dish!")
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
    review1 = Review(user1, recipe, 4, "Good!")
    review2 = Review(user2, recipe, 5, "Excellent!")
    
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
    review = Review(user, recipe, 5, "Perfect!")
    repo.add_review(review)
    
    # Reload user and verify review is tracked
    updated_user = repo.get_user('william')
    assert len(updated_user.reviews) == initial_review_count + 1


def test_review_ids_are_globally_unique(session_factory):
    """Test that review IDs are globally unique across different recipes"""
    repo = make_repo(session_factory)
    
    user = repo.get_user('william')
    recipe1 = repo.get_recipe_by_id(38)
    recipe2 = repo.get_recipe_by_id(40)
    
    # Add review to first recipe
    review1 = Review(user, recipe1, 5, "Great recipe 1!")
    repo.add_review(review1)
    
    # Add review to second recipe
    review2 = Review(user, recipe2, 4, "Great recipe 2!")
    repo.add_review(review2)
    
    # Reload recipes to get updated reviews
    updated_recipe1 = repo.get_recipe_by_id(38)
    updated_recipe2 = repo.get_recipe_by_id(40)
    
    # Find the reviews we just added
    added_review1 = [r for r in updated_recipe1.reviews if r.review_text == "Great recipe 1!"][0]
    added_review2 = [r for r in updated_recipe2.reviews if r.review_text == "Great recipe 2!"][0]
    
    # Verify IDs are different (globally unique)
    assert added_review1.id != added_review2.id
    assert added_review1.id is not None
    assert added_review2.id is not None


# FAVOURITE TESTS (there's a lot, will put in its own file soon)
# FAVOURITE TESTS
# FAVOURITE TESTS
# FAVOURITE TESTS



def test_add_and_remove_favourite(session_factory):
    """Test adding and removing a favourite"""
    repo = make_repo(session_factory)

    user = User("favuser", "password")
    repo.add_user(user)

    author = Author(601, "Fav Author")
    category = Category("Fav Category")
    recipe = Recipe(601, "Fav Recipe", author, category=category)
    repo.add_recipe(recipe)

    # Add favourite
    repo.add_favourite(user, recipe)

    # Check it exists
    assert repo.is_recipe_in_favourites("favuser", 601) == True

    # Remove favourite
    repo.remove_favourite(user, recipe)

    # Check it's gone
    assert repo.is_recipe_in_favourites("favuser", 601) == False


def test_get_user_favourites(session_factory):
    """Test retrieving user favourites"""
    repo = make_repo(session_factory)

    user = User("favuser2", "password")
    repo.add_user(user)

    author = Author(701, "Author")
    category = Category("Category")
    recipe = Recipe(701, "Recipe", author, category=category)
    repo.add_recipe(recipe)

    repo.add_favourite(user, recipe)

    favs = repo.get_user_favourites("favuser2")
    assert len(favs) >= 1
    assert any(r.id == 701 for r in favs)

def test_add_favourite_adds_recipe_to_user_favourites(session_factory):
    """
    Test that add_favourite correctly adds a recipe to a user's favourites.
    Verify that is_recipe_in_favourites returns True after adding.
    """
    repo = make_repo(session_factory)

    # Get a known user and recipe from the populated test data
    user = repo.get_user('thorke')
    assert user is not None, "Test user 'thorke' should exist in test data"

    recipe = repo.get_first_recipe()
    assert recipe is not None, "At least one recipe should exist in test data"

    recipe_id = recipe.id
    username = user.username

    # Initially should not be in favourites
    assert repo.is_recipe_in_favourites(username, recipe_id) is False

    # Add to favourites
    repo.add_favourite(user, recipe)

    # Now should be in favourites
    assert repo.is_recipe_in_favourites(username, recipe_id) is True

    # Verify it appears in get_user_favourites
    favs = repo.get_user_favourites(username)
    fav_ids = [r.id for r in favs]
    assert recipe_id in fav_ids


def test_remove_favourite_removes_recipe_from_user_favourites(session_factory):
    """
    Test that remove_favourite correctly removes a recipe from a user's favourites.
    Verify that is_recipe_in_favourites returns False after removal.
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')
    recipe = repo.get_first_recipe()

    # Add to favourites first
    repo.add_favourite(user, recipe)
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is True

    # Remove from favourites
    repo.remove_favourite(user, recipe)

    # Should no longer be in favourites
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is False

    # Verify it doesn't appear in get_user_favourites
    favs = repo.get_user_favourites(user.username)
    fav_ids = [r.id for r in favs]
    assert recipe.id not in fav_ids


def test_add_favourite_twice_does_not_create_duplicates(session_factory):
    """
    Test that adding the same recipe to favourites twice doesn't create duplicates.
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')
    recipe = repo.get_first_recipe()

    # Add to favourites twice
    repo.add_favourite(user, recipe)
    repo.add_favourite(user, recipe)

    # Should still be in favourites (no error)
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is True

    # Get favourites and count occurrences of this recipe
    favs = repo.get_user_favourites(user.username)
    count = sum(1 for r in favs if r.id == recipe.id)
    assert count == 1, "Recipe should appear exactly once in favourites"


def test_get_user_favourites_returns_recipe_objects_with_full_data(session_factory):
    """
    Test that get_user_favourites returns actual Recipe objects with all data populated
    (images, ingredients, instructions, etc.).
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')
    recipe = repo.get_first_recipe()

    # Add to favourites
    repo.add_favourite(user, recipe)

    # Get favourites
    favs = repo.get_user_favourites(user.username)

    assert len(favs) >= 1
    assert all(isinstance(r, Recipe) for r in favs)

    # Check that the favourite recipe has its data populated
    fav_recipe = next((r for r in favs if r.id == recipe.id), None)
    assert fav_recipe is not None
    assert fav_recipe.name is not None
    assert fav_recipe.author is not None
    assert fav_recipe.category is not None
    # Check that lists are populated (may be empty but should be lists)
    assert isinstance(getattr(fav_recipe, 'images', []), list)
    assert isinstance(getattr(fav_recipe, 'ingredients', []), list)
    assert isinstance(getattr(fav_recipe, 'instructions', []), list)


def test_get_user_favourites_returns_empty_list_for_user_with_no_favourites(session_factory):
    """
    Test that get_user_favourites returns an empty list for a user with no favourites.
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')

    # Ensure user has no favourites (remove any that might exist from other tests)
    # Get all recipes and remove them from favourites
    all_recipes = repo.get_recipes_paginated(page=1, per_page=10)
    for recipe in all_recipes:
        try:
            repo.remove_favourite(user, recipe)
        except Exception:
            pass

    # Now get favourites - should be empty
    favs = repo.get_user_favourites(user.username)
    assert favs == []


def test_get_user_favourites_returns_empty_for_nonexistent_user(session_factory):
    """
    Test that get_user_favourites returns an empty list for a user that doesn't exist.
    """
    repo = make_repo(session_factory)

    favs = repo.get_user_favourites('nonexistent_user_xyz')
    assert favs == []


def test_is_recipe_in_favourites_returns_false_for_nonexistent_user(session_factory):
    """
    Test that is_recipe_in_favourites returns False for a user that doesn't exist.
    """
    repo = make_repo(session_factory)

    recipe = repo.get_first_recipe()
    result = repo.is_recipe_in_favourites('nonexistent_user_xyz', recipe.id)
    assert result is False


def test_multiple_users_can_favourite_same_recipe(session_factory):
    """
    Test that multiple users can add the same recipe to their favourites independently.
    """
    repo = make_repo(session_factory)

    # Get two users (thorke exists, we need to ensure fmercury exists too)
    user1 = repo.get_user('thorke')
    user2 = repo.get_user('fmercury')

    # If fmercury doesn't exist, create them
    if user2 is None:
        from werkzeug.security import generate_password_hash
        user2 = User(username='fmercury', password=generate_password_hash('Test#6^0'))
        repo.add_user(user2)
        user2 = repo.get_user('fmercury')

    recipe = repo.get_first_recipe()

    # Both users add the same recipe to favourites
    repo.add_favourite(user1, recipe)
    repo.add_favourite(user2, recipe)

    # Both should have it in their favourites
    assert repo.is_recipe_in_favourites(user1.username, recipe.id) is True
    assert repo.is_recipe_in_favourites(user2.username, recipe.id) is True

    # Remove from user1's favourites
    repo.remove_favourite(user1, recipe)

    # user1 should not have it, but user2 should still have it
    assert repo.is_recipe_in_favourites(user1.username, recipe.id) is False
    assert repo.is_recipe_in_favourites(user2.username, recipe.id) is True


def test_user_can_have_multiple_favourites(session_factory):
    """
    Test that a user can add multiple different recipes to their favourites.
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')

    # Get 3 different recipes
    recipes = repo.get_recipes_paginated(page=1, per_page=3)
    assert len(recipes) >= 3, "Need at least 3 recipes in test data"

    recipe1, recipe2, recipe3 = recipes[0], recipes[1], recipes[2]

    # Add all three to favourites
    repo.add_favourite(user, recipe1)
    repo.add_favourite(user, recipe2)
    repo.add_favourite(user, recipe3)

    # All should be in favourites
    assert repo.is_recipe_in_favourites(user.username, recipe1.id) is True
    assert repo.is_recipe_in_favourites(user.username, recipe2.id) is True
    assert repo.is_recipe_in_favourites(user.username, recipe3.id) is True

    # Get all favourites
    favs = repo.get_user_favourites(user.username)
    fav_ids = {r.id for r in favs}

    assert recipe1.id in fav_ids
    assert recipe2.id in fav_ids
    assert recipe3.id in fav_ids
    assert len(favs) >= 3


def test_remove_favourite_with_none_values_does_not_error(session_factory):
    """
    Test that remove_favourite handles None values gracefully without errors.
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')
    recipe = repo.get_first_recipe()

    # These should not raise errors
    try:
        repo.remove_favourite(None, recipe)
        repo.remove_favourite(user, None)
        repo.remove_favourite(None, None)
    except Exception as e:
        pytest.fail(f"remove_favourite should handle None gracefully, but raised: {e}")


def test_add_favourite_with_none_values_does_not_error(session_factory):
    """
    Test that add_favourite handles None values gracefully without errors.
    """
    repo = make_repo(session_factory)

    user = repo.get_user('thorke')
    recipe = repo.get_first_recipe()

    # These should not raise errors
    try:
        repo.add_favourite(None, recipe)
        repo.add_favourite(user, None)
        repo.add_favourite(None, None)
    except Exception as e:
        pytest.fail(f"add_favourite should handle None gracefully, but raised: {e}")


def test_favourites_persist_across_repository_instances(session_factory):
    """
    Test that favourites are persisted in the database and survive across
    different repository instances (simulating app restarts).
    """
    # Create first repo instance and add a favourite
    repo1 = make_repo(session_factory)
    user = repo1.get_user('thorke')
    recipe = repo1.get_first_recipe()

    repo1.add_favourite(user, recipe)
    assert repo1.is_recipe_in_favourites(user.username, recipe.id) is True

    # Create a new repo instance (simulating app restart)
    repo2 = make_repo(session_factory)

    # Favourite should still exist
    assert repo2.is_recipe_in_favourites(user.username, recipe.id) is True

    favs = repo2.get_user_favourites(user.username)
    fav_ids = [r.id for r in favs]
    assert recipe.id in fav_ids



# SEARCH TESTS (there's a lot, will put in its own file soon)
# SEARCH TESTS
# SEARCH TESTS
# SEARCH TESTS

def test_search_by_name(session_factory):
    """Test searching recipes by name"""
    repo = make_repo(session_factory)

    first = repo.get_first_recipe()
    assert first is not None

    # Search for part of the name
    term = first.name[:5].lower()
    results = repo.get_recipes_by_name(term)

    # Should find at least the first recipe
    assert len(results) > 0
    assert any(r.id == first.id for r in results)

def test_search_by_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    # Pick a known recipe and derive a partial, lowercased search term from its name
    first = repo.get_first_recipe()
    assert first is not None and first.name
    term = first.name[: max(1, len(first.name) // 3)].lower()

    results = repo.get_recipes_by_name(term)
    names = {getattr(r, 'name', '').lower() for r in results}

    assert first.name.lower() in names
    # sanity : calling paginated variant should also include it when page is large enough
    page_results = repo.get_recipes_by_name_paginated(term, page=1, per_page=50)
    page_names = {getattr(r, 'name', '').lower() for r in page_results}
    assert first.name.lower() in page_names


def test_search_by_author_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    # Use the author of a known recipe to create a search term
    first = repo.get_first_recipe()
    assert first is not None and getattr(first, 'author', None) is not None
    author_name = getattr(first.author, 'name', '')
    assert author_name
    term = author_name[: max(1, len(author_name) // 3)].lower()

    results = repo.get_recipes_by_author_name(term)
    ids = {getattr(r, 'id', None) for r in results}
    assert first.id in ids

    # If paginated search exists, it should also find it
    if hasattr(repo, 'get_recipes_by_author_name_paginated'):
        page_results = repo.get_recipes_by_author_name_paginated(term, page=1, per_page=50)
        page_ids = {getattr(r, 'id', None) for r in page_results}
        assert first.id in page_ids


def test_search_by_category_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    first = repo.get_first_recipe()
    assert first is not None and getattr(first, 'category', None) is not None
    category_name = getattr(first.category, 'name', '')
    assert category_name
    term = category_name[: max(1, len(category_name) // 3)].lower()

    results = repo.get_recipes_by_category_name(term)
    ids = {getattr(r, 'id', None) for r in results}
    assert first.id in ids

    # Test paginated variant if available
    if hasattr(repo, 'get_recipes_by_category_name_paginated'):
        page_results = repo.get_recipes_by_category_name_paginated(term, page=1, per_page=50)
        page_ids = {getattr(r, 'id', None) for r in page_results}
        assert first.id in page_ids


def test_search_by_ingredient_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    # Ensure we have a recipe with ingredients loaded
    first = repo.get_first_recipe()
    assert first is not None
    # If no ingredients are present on this recipe, fetch another that has some using a simple scan
    candidate = first
    if not getattr(candidate, 'ingredients', None):
        # Scan a small first page; adjust if needed
        page = repo.get_recipes_paginated(page=1, per_page=25)
        for r in page:
            if getattr(r, 'ingredients', None):
                candidate = r
                break
    ings = getattr(candidate, 'ingredients', [])
    assert ings, "No ingredients found on scanned recipes; check populate() filled RecipeIngredient table."

    ing = str(ings[0])
    term = ing[: max(1, len(ing) // 3)].lower()

    results = repo.get_recipes_by_ingredient_name(term)
    ids = {getattr(r, 'id', None) for r in results}
    assert candidate.id in ids

    # Test paginated variant if available
    if hasattr(repo, 'get_recipes_by_ingredient_name_paginated'):
        page_results = repo.get_recipes_by_ingredient_name_paginated(term, page=1, per_page=50)
        page_ids = {getattr(r, 'id', None) for r in page_results}
        assert candidate.id in page_ids




# Other/misc tests
def test_count_recipes(session_factory):
    """Test counting recipes"""
    repo = make_repo(session_factory)
    count = repo.count_recipes()

    assert count > 0


def test_get_featured_recipes(session_factory):
    """Test getting featured recipes"""
    repo = make_repo(session_factory)
    featured = repo.get_featured_recipes(limit=5)

    assert len(featured) <= 5
    assert len(featured) > 0


# py -m pytest -v tests_db/unit/test_database_repository.py




import pytest

from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.domainmodel.user import User
from recipe.domainmodel.recipe import Recipe


def make_repo(session_factory) -> SqlAlchemyRepository:
    return SqlAlchemyRepository(session_factory)


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
def test_get_user_favourites_returns_empty_for_nonexistent_user(session_factory):
    """
    Test that get_user_favourites returns an empty list for a user that doesn't exist.
    """
    repo = make_repo(session_factory)

    favs = repo.get_user_favourites('nonexistent_user_xyz')
    assert favs == []


@pytest.mark.db
def test_is_recipe_in_favourites_returns_false_for_nonexistent_user(session_factory):
    """
    Test that is_recipe_in_favourites returns False for a user that doesn't exist.
    """
    repo = make_repo(session_factory)

    recipe = repo.get_first_recipe()
    result = repo.is_recipe_in_favourites('nonexistent_user_xyz', recipe.id)
    assert result is False


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
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


@pytest.mark.db
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


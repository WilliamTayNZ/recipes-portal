import pytest

from recipe.adapters.memory_repository import MemoryRepository
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.user import User


# Tests for MemoryRepository favourites behaviour

def test_add_and_remove_favourite_updates_user_favourites():
    """
    GIVEN a MemoryRepository, a User and a Recipe
    WHEN the repository adds the recipe to the user's favourites and later removes it
    THEN the user's favourite list and is_recipe_in_favourites reflect the changes
    """
    repo = MemoryRepository()

    # Create author/category/recipe/user
    author = Author(author_id=10, name="Test Author")
    category = Category(name="Dessert", recipes=[], category_id=5)
    recipe = Recipe(recipe_id=501, name="Test Cake", author=author, description="desc", category=category)
    user = User(username="tester", password="pw", user_id=77)

    # Add to repo
    repo.add_user(user)
    repo.add_author(author)
    repo.add_category(category)
    repo.add_recipe(recipe)

    # Initially not in favourites
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is False
    assert repo.get_user_favourites(user.username) == []

    # Add favourite
    repo.add_favourite(user, recipe)
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is True
    favs = repo.get_user_favourites(user.username)
    assert len(favs) == 1 and favs[0] is recipe

    # Remove favourite
    repo.remove_favourite(user, recipe)
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is False
    assert repo.get_user_favourites(user.username) == []


def test_get_user_favourites_returns_empty_for_unknown_user():
    """
    Ensure that requesting favourites for an unknown username returns an empty list instead of raising.
    """
    repo = MemoryRepository()
    assert repo.get_user_favourites("nonexistent") == []


def test_add_favourite_handles_none_gracefully():
    """
    Confirm that add_favourite/remove_favourite do nothing (no exception) when given None values.
    """
    repo = MemoryRepository()
    # Should not raise
    repo.add_favourite(None, None)
    repo.remove_favourite(None, None)


def test_is_recipe_in_favourites_for_missing_user_returns_false():
    """
    If the username does not exist in the repository, is_recipe_in_favourites should return False.
    """
    repo = MemoryRepository()
    assert repo.is_recipe_in_favourites('no_user', 12345) is False


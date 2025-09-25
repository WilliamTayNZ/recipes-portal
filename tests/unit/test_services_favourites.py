import pytest

from recipe.adapters.memory_repository import MemoryRepository
import recipe.blueprints.browse.services as services
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.user import User
from recipe.domainmodel.favourite import Favourite


# ----------------------- Helper factory -----------------------
def make_repo_with_recipe(recipe_id=1001, username='tester'):
    repo = MemoryRepository()
    author = Author(author_id=1, name='Author One')
    category = Category(name='Dessert', recipes=[], category_id=1)
    recipe = Recipe(recipe_id=recipe_id, name='A Cake', author=author, description='Tasty', category=category)
    user = User(username=username, password='pw', user_id=11)

    # add to repo
    repo.add_user(user)
    repo.add_author(author)
    repo.add_category(category)
    repo.add_recipe(recipe)

    return repo, user, recipe


# ----------------------- Tests for toggle_favourite -----------------------

def test_toggle_favourite_returns_false_when_user_not_authenticated(monkeypatch):
    """
    If there is no authenticated user, toggle_favourite should return False.
    """
    repo, user, recipe = make_repo_with_recipe()

    # simulate not authenticated
    anon = User(username='anon', password='x', user_id=2)
    anon.is_authenticated = False
    monkeypatch.setattr(services, 'current_user', anon)

    result = services.toggle_favourite(recipe.id, repo)
    assert result is False


def test_toggle_favourite_returns_false_for_missing_recipe(monkeypatch):
    """
    If the recipe id does not exist in the repository, toggle_favourite should return False.
    """
    repo = MemoryRepository()
    user = User(username='u1', password='x', user_id=3)
    user.is_authenticated = True
    repo.add_user(user)

    monkeypatch.setattr(services, 'current_user', user)

    # recipe id 9999 not present
    result = services.toggle_favourite(9999, repo)
    assert result is False


def test_toggle_favourite_adds_and_removes_favourite(monkeypatch):
    """
    Ensure toggle_favourite adds a favourite when not present and removes it when present.
    Test covers both add (returns True) and remove (returns False) flows and repo state changes.
    """
    repo, user, recipe = make_repo_with_recipe(recipe_id=2002, username='favtester')
    user.is_authenticated = True
    monkeypatch.setattr(services, 'current_user', user)

    # Initially not favourited
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is False

    # Toggle should add
    added = services.toggle_favourite(recipe.id, repo)
    assert added is True
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is True

    # Toggling again should remove
    removed = services.toggle_favourite(recipe.id, repo)
    assert removed is False
    assert repo.is_recipe_in_favourites(user.username, recipe.id) is False


# ----------------------- Tests for annotate_is_favourite -----------------------

def test_annotate_is_favourite_sets_flag_for_authenticated_user(monkeypatch):
    """
    Given a logged-in user with one favourite, annotate_is_favourite should mark the matching recipe's
    `is_favourite` attribute True and others False.
    """
    repo, user, recipe = make_repo_with_recipe(recipe_id=3003, username='anno')
    user.is_authenticated = True
    # Add favourite object to the user
    repo.add_favourite(user, recipe)

    # create another recipe not favourited
    author2 = Author(author_id=2, name='Other')
    category2 = Category(name='OtherCat', recipes=[], category_id=2)
    recipe2 = Recipe(recipe_id=3004, name='Other Recipe', author=author2, description='', category=category2)
    repo.add_author(author2)
    repo.add_category(category2)
    repo.add_recipe(recipe2)

    monkeypatch.setattr(services, 'current_user', user)

    recipes = [recipe, recipe2]
    services.annotate_is_favourite(recipes, repo)

    assert getattr(recipes[0], 'is_favourite', False) is True
    assert getattr(recipes[1], 'is_favourite', False) is False


def test_annotate_is_favourite_sets_false_when_not_authenticated(monkeypatch):
    """
    When no user is logged in, annotate_is_favourite must set is_favourite False on all recipes.
    """
    repo, user, recipe = make_repo_with_recipe()
    anon = User(username='anon2', password='x', user_id=55)
    anon.is_authenticated = False
    monkeypatch.setattr(services, 'current_user', anon)

    recipes = [recipe]
    services.annotate_is_favourite(recipes, repo)
    assert getattr(recipes[0], 'is_favourite', True) is False


# ----------------------- Tests for get_favourites and search_favourites -----------------------

def test_get_favourites_returns_recipes_for_authenticated_user(monkeypatch):
    """
    When the user has favourites, get_favourites should return a list of Recipe objects. If none, it raises.
    """
    repo, user, recipe = make_repo_with_recipe(recipe_id=4004, username='favlist')
    user.is_authenticated = True
    repo.add_favourite(user, recipe)
    monkeypatch.setattr(services, 'current_user', user)

    favs = services.get_favourites(repo)
    assert isinstance(favs, list)
    assert favs and favs[0].id == recipe.id


def test_get_favourites_raises_when_no_favourites(monkeypatch):
    """
    If the authenticated user has no favourites, get_favourites should raise NonExistentRecipeException.
    """
    repo, user, recipe = make_repo_with_recipe(recipe_id=5005, username='emptyfav')
    user.is_authenticated = True
    # no favourite added
    monkeypatch.setattr(services, 'current_user', user)

    with pytest.raises(services.NonExistentRecipeException):
        services.get_favourites(repo)


def test_search_favourites_filters_by_name(monkeypatch):
    """
    Ensure search_favourites can filter the user's favourites by recipe name (case-insensitive).
    """
    repo, user, recipe = make_repo_with_recipe(recipe_id=6006, username='searcher')
    user.is_authenticated = True
    repo.add_favourite(user, recipe)
    monkeypatch.setattr(services, 'current_user', user)

    results = services.search_favourites('name', 'cake', repo)
    assert len(results) == 1 and results[0].id == recipe.id

    # searching for a non-matching query should raise
    with pytest.raises(services.NonExistentRecipeException):
        services.search_favourites('name', 'nonexistent', repo)


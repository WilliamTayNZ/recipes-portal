import pytest
from pathlib import Path

from recipe.adapters.repository import RepositoryException
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe


# ---------- Fixtures ----------
@pytest.fixture
def author_alice() -> Author:
    return Author(author_id=1, name="Alice")

@pytest.fixture
def author_bob() -> Author:
    return Author(author_id=2, name="Bob")

@pytest.fixture
def cat_dessert() -> Category:
    return Category(name="Dessert", category_id=10)

@pytest.fixture
def cat_drink() -> Category:
    return Category(name="Drink", category_id=11)

@pytest.fixture
def recipe_1(author_alice, cat_dessert) -> Recipe:
    return Recipe(
        recipe_id=101,
        name="Brownies",
        author=author_alice,
        description="Rich and fudgy.",
        category=cat_dessert,
        ingredients=["flour", "cocoa", "butter", "sugar"],
        instructions=["Mix", "Bake"],
    )

@pytest.fixture
def recipe_2(author_alice, cat_drink) -> Recipe:
    return Recipe(
        recipe_id=102,
        name="Iced Latte",
        author=author_alice,
        description="Coffee + milk + ice.",
        category=cat_drink,
        ingredients=["espresso", "milk", "ice"],
        instructions=["Pour", "Stir"],
    )

@pytest.fixture
def recipe_3(author_bob, cat_dessert) -> Recipe:
    return Recipe(
        recipe_id=103,
        name="Cheesecake",
        author=author_bob,
        description="Creamy classic.",
        category=cat_dessert,
        ingredients=["cream cheese", "eggs", "sugar"],
        instructions=["Beat", "Bake"],
    )

# Recipe tests

def test_repository_can_add_and_get_recipe_by_id(in_memory_repo, recipe_1):
    in_memory_repo.add_recipe(recipe_1)
    assert in_memory_repo.get_recipe(101) is recipe_1

def test_repository_returns_none_when_get_recipe_by_id_missing(in_memory_repo):
    assert in_memory_repo.get_recipe(9999) is None

def test_repository_raises_for_duplicate_recipe_id(in_memory_repo,recipe_1):

    #recipe_1 = Recipe(101,"Brownies",  Author(1, "Brownies"))

    in_memory_repo.add_recipe(recipe_1)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_recipe(recipe_1)

# Author tests

def test_repository_can_add_author_and_get_by_id(in_memory_repo, author_alice):
    in_memory_repo.add_author(author_alice)
    assert in_memory_repo.get_author(1) is author_alice

def test_repository_rejects_non_author_on_add(in_memory_repo):
    with pytest.raises(TypeError):
        in_memory_repo.add_author("$$$$")

def test_repository_raises_for_duplicate_author_id(in_memory_repo, author_alice):
    in_memory_repo.add_author(author_alice)
    with pytest.raises(RepositoryException):
        in_memory_repo.add_author(author_alice)

def test_repository_raises_for_missing_author_name(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_author('Mihir Patil')

def test_repository_can_get_recipes_by_author(in_memory_repo, recipe_1, recipe_2, author_alice):
    in_memory_repo.add_recipe(recipe_1)
    in_memory_repo.add_recipe(recipe_2)
    recipes = in_memory_repo.get_recipes_by_author(author_alice.name)
    names = sorted(r.name for r in recipes)
    assert len(recipes) == 2

def test_repository_raises_for_missing_author_in_get_recipes_by_author_id(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_recipes_by_author_id(999)

# Category tests

def test_repository_can_add_category_and_get_by_id(in_memory_repo, cat_dessert):
    in_memory_repo.add_category(cat_dessert)
    assert in_memory_repo.get_category(10) is cat_dessert

def test_repository_rejects_non_category_on_add(in_memory_repo):
    with pytest.raises(TypeError):
        in_memory_repo.add_category("Agile Methodologies")

def test_repository_raises_for_duplicate_category_id(in_memory_repo, cat_dessert):
    in_memory_repo.add_category(cat_dessert)
    with pytest.raises(RepositoryException):
        in_memory_repo.add_category(cat_dessert)

def test_repository_raises_for_missing_category_id(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_category(404)

def test_repository_can_get_recipes_by_category(in_memory_repo, recipe_1, recipe_3, cat_dessert):
    in_memory_repo.add_category(cat_dessert)
    in_memory_repo.add_recipe(recipe_1)
    in_memory_repo.add_recipe(recipe_3)
    recipes = in_memory_repo.get_recipes_by_category(cat_dessert.id)
    names = sorted(r.name for r in recipes)
    assert names == ["Brownies", "Cheesecake"]

def test_repository_raises_for_missing_category_in_get_recipes_by_category(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_recipes_by_category(999999)

# python -m pytest -v tests
# py -m pytest -v tests/unit/test_memory_repository.py
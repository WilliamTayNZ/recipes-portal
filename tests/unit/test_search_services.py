import pytest

from recipe.adapters.memory_repository import MemoryRepository
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe
from recipe.blueprints.browse import services


@pytest.fixture
def repo_with_data() -> MemoryRepository:
    repo = MemoryRepository()

    # Authors
    alice = Author(author_id=1, name="Alice")
    bob = Author(author_id=2, name="Bob")
    repo.add_author(alice)
    repo.add_author(bob)

    # Categories
    dessert = Category(name="Dessert", category_id=10)
    drink = Category(name="Drink", category_id=11)
    repo.add_category(dessert)
    repo.add_category(drink)

    # Recipes
    r1 = Recipe(
        recipe_id=101,
        name="Brownies",
        author=alice,
        description="Rich and fudgy.",
        category=dessert,
        ingredients=["flour", "cocoa", "butter", "sugar"],
        instructions=["Mix", "Bake"],
    )
    r2 = Recipe(
        recipe_id=102,
        name="Iced Latte",
        author=alice,
        description="Coffee + milk + ice.",
        category=drink,
        ingredients=["espresso", "milk", "ice"],
        instructions=["Pour", "Stir"],
    )
    r3 = Recipe(
        recipe_id=103,
        name="Cheesecake",
        author=bob,
        description="Creamy classic.",
        category=dessert,
        ingredients=["cream cheese", "eggs", "sugar"],
        instructions=["Beat", "Bake"],
    )

    repo.add_recipe(r1)
    repo.add_recipe(r2)
    repo.add_recipe(r3)
    return repo


def test_search_by_name(repo_with_data: MemoryRepository):
    results = services.search_recipes("name", "brown", repo_with_data)
    names = sorted(r.name for r in results)
    assert names == ["Brownies"]


def test_search_by_author(repo_with_data: MemoryRepository):
    results = services.search_recipes("author", "alice", repo_with_data)
    names = sorted(r.name for r in results)
    assert names == ["Brownies", "Iced Latte"]


def test_search_by_category(repo_with_data: MemoryRepository):
    results = services.search_recipes("category", "dess", repo_with_data)
    names = sorted(r.name for r in results)
    assert names == ["Brownies", "Cheesecake"]


def test_search_by_ingredient(repo_with_data: MemoryRepository):
    results = services.search_recipes("ingredient", "sugar", repo_with_data)
    names = sorted(r.name for r in results)
    assert names == ["Brownies", "Cheesecake"]


def test_search_no_results_raises(repo_with_data: MemoryRepository):
    with pytest.raises(services.NonExistentRecipeException):
        services.search_recipes("name", "does-not-exist", repo_with_data)



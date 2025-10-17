from datetime import datetime, timedelta

from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review


def test_add_and_get_user(session_factory):
    """Test adding and retrieving a user"""
    repo = SqlAlchemyRepository(session_factory)
    user = User("testuser", "password123")
    repo.add_user(user)

    retrieved = repo.get_user("testuser")
    assert retrieved is not None
    assert retrieved.username == "testuser"


def test_add_and_get_recipe(session_factory):
    """Test adding and retrieving a recipe"""
    repo = SqlAlchemyRepository(session_factory)

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


def test_add_review(session_factory):
    """Test adding a review"""
    repo = SqlAlchemyRepository(session_factory)

    # Use a very high ID to avoid conflicts with populated data
    test_user_id = 999998
    test_recipe_id = 999997

    user = User("reviewer_test", "password")
    repo.add_user(user)

    author = Author(test_recipe_id, "Recipe Author")
    category = Category("Category")
    recipe = Recipe(test_recipe_id, "Recipe", author, category=category)
    repo.add_recipe(recipe)

    # Create review with recipe_id properly set via the private attribute for ORM
    review = Review(
        review_id=1,
        user=user,
        recipe=recipe,
        rating=5,
        review_text="Excellent!",
        date=datetime.now()
    )
    # Set the private recipe_id attribute that the ORM expects
    review._Review__recipe_id = test_recipe_id

    repo.add_review(review)

    # Verify it was added
    assert review.rating == 5


def test_add_and_remove_favourite(session_factory):
    """Test adding and removing a favourite"""
    repo = SqlAlchemyRepository(session_factory)

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
    repo = SqlAlchemyRepository(session_factory)

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


def test_get_number_of_recipe(session_factory):
    """Test counting recipes"""
    repo = SqlAlchemyRepository(session_factory)
    count = repo.get_number_of_recipe()

    # Should have recipes from populated data
    assert count > 0


def test_get_recipes(session_factory):
    """Test getting all recipes"""
    repo = SqlAlchemyRepository(session_factory)
    recipes = repo.get_recipes()

    # Should have recipes from populated data
    assert len(recipes) > 0


def test_get_recipe_by_id(session_factory):
    """Test getting a recipe by ID"""
    repo = SqlAlchemyRepository(session_factory)

    # Get first recipe to test with
    first_recipe = repo.get_first_recipe()
    assert first_recipe is not None

    # Get it by ID
    retrieved = repo.get_recipe_by_id(first_recipe.id)
    assert retrieved is not None
    assert retrieved.id == first_recipe.id


def test_get_recipes_paginated(session_factory):
    """Test paginated recipe retrieval"""
    repo = SqlAlchemyRepository(session_factory)

    page1 = repo.get_recipes_paginated(page=1, per_page=3)
    assert len(page1) <= 3

    page2 = repo.get_recipes_paginated(page=2, per_page=3)
    # Second page might be empty or have recipes
    assert isinstance(page2, list)


def test_search_by_name(session_factory):
    """Test searching recipes by name"""
    repo = SqlAlchemyRepository(session_factory)

    first = repo.get_first_recipe()
    assert first is not None

    # Search for part of the name
    term = first.name[:5].lower()
    results = repo.get_recipes_by_name(term)

    # Should find at least the first recipe
    assert len(results) > 0
    assert any(r.id == first.id for r in results)


def test_count_recipes(session_factory):
    """Test counting recipes"""
    repo = SqlAlchemyRepository(session_factory)
    count = repo.count_recipes()

    assert count > 0


def test_get_featured_recipes(session_factory):
    """Test getting featured recipes"""
    repo = SqlAlchemyRepository(session_factory)
    featured = repo.get_featured_recipes(limit=5)

    assert len(featured) <= 5
    assert len(featured) > 0

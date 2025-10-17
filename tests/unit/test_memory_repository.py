import pytest
from pathlib import Path

from recipe.adapters.repository import RepositoryException
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe

from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review

# ---------- Fixtures ----------
@pytest.fixture
def author_alice() -> Author:
    return Author(author_id=1, name="Alice")

@pytest.fixture
def author_bob() -> Author:
    return Author(author_id=2, name="Bob")

@pytest.fixture
def cat_confectionary() -> Category:
    return Category(name="Confectionary", recipes=[], category_id=1)

@pytest.fixture
def cat_drink() -> Category:
    return Category(name="Drink", recipes=[], category_id=2)

@pytest.fixture
def recipe_1(author_alice, cat_confectionary) -> Recipe:
    return Recipe(
        recipe_id=101,
        name="Brownies",
        author=author_alice,
        description="Rich and fudgy.",
        category=cat_confectionary,
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
def recipe_3(author_bob, cat_confectionary) -> Recipe:
    return Recipe(
        recipe_id=103,
        name="Cheesecake",
        author=author_bob,
        description="Creamy classic.",
        category=cat_confectionary,
        ingredients=["cream cheese", "eggs", "sugar"],
        instructions=["Beat", "Bake"],
    )

# Recipe tests

def test_repository_can_add_and_get_recipe_by_id(in_memory_repo, recipe_1):
    in_memory_repo.add_recipe(recipe_1)
    assert in_memory_repo.get_recipe_by_id(101) is recipe_1

def test_repository_returns_none_when_get_recipe_by_id_missing(in_memory_repo):
    assert in_memory_repo.get_recipe_by_id(9999) is None

def test_repository_raises_for_duplicate_recipe_id(in_memory_repo,recipe_1):

    #recipe_1 = Recipe(101,"Brownies",  Author(1, "Brownies"))

    in_memory_repo.add_recipe(recipe_1)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_recipe(recipe_1)

# Author tests

def test_repository_can_add_author_and_get_by_id(in_memory_repo, author_alice):
    in_memory_repo.add_author(author_alice)
    assert in_memory_repo.get_author_by_id(1) is author_alice

def test_repository_can_add_author_and_get_by_name(in_memory_repo, author_alice):
    in_memory_repo.add_author(author_alice)
    assert in_memory_repo.get_authors_by_name("Alice")[0] is author_alice

def test_repository_can_get_2_authors_with_same_name(in_memory_repo):
    assert len(in_memory_repo.get_authors_by_name("Diana Adams")) == 2

def test_repository_rejects_non_author_on_add(in_memory_repo):
    with pytest.raises(TypeError):
        in_memory_repo.add_author("$$$$")

def test_repository_raises_for_duplicate_author_id(in_memory_repo, author_alice):
    in_memory_repo.add_author(author_alice)
    with pytest.raises(RepositoryException):
        in_memory_repo.add_author(author_alice)


def test_repository_raises_for_missing_author_name(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_authors_by_name('Mihir Patil')

def test_repository_can_get_recipes_by_author_name(in_memory_repo, recipe_1, recipe_2, author_alice):
    in_memory_repo.add_recipe(recipe_1)
    in_memory_repo.add_recipe(recipe_2)
    recipes = in_memory_repo.get_recipes_by_author_name(author_alice.name)
    names = sorted(r.name for r in recipes)
    assert len(recipes) == 2

def test_repository_raises_for_missing_author_in_get_recipes_by_author_id(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_recipes_by_author_id(999)

# Category tests

def test_repository_can_add_category_and_get_by_name(in_memory_repo, cat_confectionary):
    in_memory_repo.add_category(cat_confectionary)
    assert in_memory_repo.get_category_by_name("Confectionary") is cat_confectionary

def test_repository_rejects_non_category_on_add(in_memory_repo):
    with pytest.raises(TypeError):
        in_memory_repo.add_category("Agile Methodologies")

def test_repository_raises_for_duplicate_category_name(in_memory_repo, cat_confectionary):
    in_memory_repo.add_category(cat_confectionary)
    with pytest.raises(RepositoryException):
        in_memory_repo.add_category(cat_confectionary)

def test_repository_raises_for_missing_category_name(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_category_by_name("404")

def test_repository_can_get_recipes_by_category_name(in_memory_repo, recipe_1, recipe_3, cat_confectionary):
    in_memory_repo.add_category(cat_confectionary)
    in_memory_repo.add_recipe(recipe_1)
    in_memory_repo.add_recipe(recipe_3)
    recipes = in_memory_repo.get_recipes_by_category_name(cat_confectionary.name)
    names = sorted(r.name for r in recipes)
    assert names == ["Brownies", "Cheesecake"]

def test_repository_raises_for_missing_category_in_get_recipes_by_category_name(in_memory_repo):
    with pytest.raises(RepositoryException):
        in_memory_repo.get_recipes_by_category_name("Iron II")

# "Integration" test, i.e that the units work together

def test_repository_links_recipe_with_author_and_category(in_memory_repo, recipe_2, author_alice, cat_drink):
    in_memory_repo.add_author(author_alice)
    in_memory_repo.add_category(cat_drink)
    in_memory_repo.add_recipe(recipe_2)

    author = in_memory_repo.get_author_by_id(author_alice.id)
    category = in_memory_repo.get_category_by_name(cat_drink.name)

    print(f"Author: {author}")
    print(f"Category: {category}")

    print(f"Recipe 2: {recipe_2}")
    print(f"Author recipes: {author.recipes}")
    print(f"Category recipes: {category.recipes}")

    assert recipe_2 in author.recipes
    assert recipe_2 in category.recipes


# ---------- Review Tests ----------
def test_delete_review_updates_recipe_rating(in_memory_repo):
    user1 = User('user1', 'password123')
    user2 = User('user2', 'password456')
    in_memory_repo.add_user(user1)
    in_memory_repo.add_user(user2)

    recipe = in_memory_repo.get_first_recipe()
    assert recipe is not None
    
    # Add three reviews with different ratings
    review1 = Review(review_id=1, user=user1, recipe=recipe, rating=5, review_text="Excellent!")
    review2 = Review(review_id=2, user=user2, recipe=recipe, rating=3, review_text="OK")
    review3 = Review(review_id=3, user=user1, recipe=recipe, rating=4, review_text="Good")
    
    in_memory_repo.add_review(review1)
    in_memory_repo.add_review(review2)
    in_memory_repo.add_review(review3)
    
    # Rating should be (5 + 3 + 4) / 3 = 4.0
    assert recipe.rating == 4.0
    
    # Delete the 5-star review
    success = in_memory_repo.delete_review(review1.id, user1.username)
    assert success is True
    
    # Rating should now be (3 + 4) / 2 = 3.5
    assert recipe.rating == 3.5
    
    # Delete another review
    success = in_memory_repo.delete_review(review2.id, user2.username)
    assert success is True
    
    # Rating should now be 4 / 1 = 4.0
    assert recipe.rating == 4.0
    
    # Delete the last review
    success = in_memory_repo.delete_review(review3.id, user1.username)
    assert success is True
    
    # No reviews left, rating should be None
    assert recipe.rating is None


def test_review_id_no_collision_after_deletion(in_memory_repo):
    """
    Test that reproduces the 403 bug: Review IDs should not be reused after deletion.
    This follows the exact sequence that caused the bug:
    1. Add 2 reviews to recipe A
    2. Delete review 1
    3. Add 2 reviews to recipe B (should get IDs 3 and 4, NOT reuse 1 and 2)
    4. Delete review 2
    5. Add another review to recipe B (should get ID 5, NOT reuse 2)
    6. Try to delete the new review - should succeed
    """
    user = in_memory_repo.get_user('thorke')
    recipe_a = in_memory_repo.get_recipe_by_id(38)
    recipe_b = in_memory_repo.get_recipe_by_id(40)
    
    # Step 1: Add 2 reviews to recipe A
    review1 = Review(user, recipe_a, 5, "First review")
    review2 = Review(user, recipe_a, 4, "Second review")
    in_memory_repo.add_review(review1)
    in_memory_repo.add_review(review2)
    
    assert review1.id == 1
    assert review2.id == 2
    
    # Step 2: Delete review 1
    success = in_memory_repo.delete_review(1, user.username)
    assert success is True
    
    # Step 3: Add 2 reviews to recipe B
    # These should get IDs 3 and 4, NOT 1 and 2
    review3 = Review(user, recipe_b, 5, "Third review")
    review4 = Review(user, recipe_b, 4, "Fourth review")
    in_memory_repo.add_review(review3)
    in_memory_repo.add_review(review4)
    
    # CRITICAL: IDs should NOT be reused
    assert review3.id == 3, f"Expected ID 3, got {review3.id} - ID collision detected!"
    assert review4.id == 4, f"Expected ID 4, got {review4.id} - ID collision detected!"
    
    # Step 4: Delete review 2 (from recipe A)
    success = in_memory_repo.delete_review(2, user.username)
    assert success is True
    
    # Step 5: Add another review to recipe B
    # Should get ID 5, NOT reuse ID 2
    review5 = Review(user, recipe_b, 3, "Fifth review")
    in_memory_repo.add_review(review5)
    
    # CRITICAL: Should not reuse ID 2
    assert review5.id == 5, f"Expected ID 5, got {review5.id} - ID collision detected!"
    
    # Step 6: Try to delete review5 - should succeed
    # This was the bug: if ID was reused (ID=2), this would fail with 403
    # because it would try to delete a different review with the same ID
    success = in_memory_repo.delete_review(review5.id, user.username)
    assert success is True, "Failed to delete review - likely due to ID collision bug!"
    
    # Verify the review is actually deleted
    recipe_b_updated = in_memory_repo.get_recipe_by_id(40)
    review_texts = [r.review_text for r in recipe_b_updated.reviews]
    assert "Fifth review" not in review_texts


# python -m pytest -v tests
# py -m pytest -v tests/unit/test_memory_repository.py
# py -m pytest -v tests/unit/test_memory_repository.py::test_review_id_no_collision_after_deletion
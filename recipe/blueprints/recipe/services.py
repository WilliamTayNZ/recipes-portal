from typing import List, Iterable

from recipe.adapters.repository import AbstractRepository
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review


class NonExistentRecipeException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_review(recipe_id: int, review_text: str, rating: float, user_name: str, repo: AbstractRepository):
    # Check that the recipe exists.
    recipe = repo.get_recipe_by_id(recipe_id)
    if recipe is None:
        raise NonExistentRecipeException

    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    # Get next review ID
    review_id = len(recipe.reviews) + 1
    
    # Create new review with the given rating and text
    rating = float(rating)  # Convert rating to float
    review = Review(review_id, user, recipe, rating, review_text)

    # Add review to repository (which will add it to the recipe)
    repo.add_review(review)
    
    return review


def get_reviews_for_recipe(recipe_id: int, repo: AbstractRepository) -> List[Review]:
    """Get all reviews for a recipe sorted by date (most recent first)."""
    recipe = repo.get_recipe_by_id(recipe_id)
    if recipe is None:
        raise NonExistentRecipeException
    return sorted(recipe.reviews, key=lambda r: r.date, reverse=True)

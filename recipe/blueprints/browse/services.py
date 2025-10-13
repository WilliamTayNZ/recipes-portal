from typing import List
from flask_login import current_user
from recipe.adapters.repository import AbstractRepository
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.recipe import Recipe

class NonExistentRecipeException(Exception):
    pass

class UnknownUserException(Exception):
    pass

def get_recipe(recipe_id: int, repo: AbstractRepository):
    recipe = repo.get_recipe_by_id(recipe_id)
    if recipe is None:
        raise NonExistentRecipeException(f"Recipe with id {recipe_id} does not exist.")
    return recipe

def get_recipes_by_name(name: str, repo: AbstractRepository):
    recipes = repo.get_recipes_by_name(name)
    if not recipes:
        raise NonExistentRecipeException(f"No recipes found with name containing '{name}'.")
    return recipes

def get_recipes_paginated(page: int, per_page: int, repo: AbstractRepository):
    """
    Service function: Get recipes with pagination for browse page.
    
    This function provides a service layer wrapper around the repository's
    pagination functionality, handling exceptions appropriately.
    
    Args:
        page: Page number (1-based)
        per_page: Number of recipes per page
        repo: Repository instance (database or memory)
        
    Returns:
        List of Recipe objects for the specified page
        
    Raises:
        NonExistentRecipeException: If no recipes found on the requested page
    """
    recipes = repo.get_recipes_paginated(page, per_page)
    if not recipes:
        raise NonExistentRecipeException("No recipes found.")
    return recipes

def search_recipes_paginated(filter_by: str, query: str, page: int, per_page: int, repo: AbstractRepository):
    """Search recipes with pagination and exception handling"""
    query = query.lower()
    recipes = repo.get_recipes_by_name_paginated(query, page, per_page)
    if not recipes:
        raise NonExistentRecipeException(f"No recipes found with name containing '{query}'.")
    return recipes

def count_recipes(repo: AbstractRepository):
    """Get total recipe count"""
    return repo.count_recipes()

def count_recipes_by_name(name: str, repo: AbstractRepository):
    """Get count of recipes matching name"""
    return repo.count_recipes_by_name(name)

def search_recipes(filter_by: str, query: str, repo: AbstractRepository):
    query = query.lower()

    # Use existing function to get all recipes by passing empty string
    all_recipes = get_recipes_by_name("", repo)

    filtered = []

    for recipe in all_recipes:
        if filter_by == "name" and query in (getattr(recipe, "name", "") or "").lower():
            filtered.append(recipe)
        elif filter_by == "category":
            category_name = getattr(getattr(recipe, "category", None), "name", "") or ""
            if query in category_name.lower():
                filtered.append(recipe)
        elif filter_by == "author":
            author_name = getattr(getattr(recipe, "author", None), "name", "") or ""
            if query in author_name.lower():
                filtered.append(recipe)
        elif filter_by == "ingredient":
            ingredients = getattr(recipe, "ingredients", []) or []
            if any(query in (ing or "").lower() for ing in ingredients):
                filtered.append(recipe)

    if not filtered:
        raise NonExistentRecipeException(f"No recipes found for {filter_by} containing '{query}'.")

    return filtered


def _require_user():
    if not getattr(current_user, 'is_authenticated', False):
        raise UnknownUserException("User must be logged in")
    return current_user


def _current_user_identifier() -> str:
    user = _require_user()
    get_id = getattr(user, 'get_id', None)
    return get_id() if callable(get_id) else getattr(user, 'username')


def annotate_is_favourite(recipes: List[Recipe], repo: AbstractRepository) -> None:
    if not getattr(current_user, 'is_authenticated', False):
        for r in recipes:
            setattr(r, 'is_favourite', False)
        return
    user = current_user
    fav_recipe_ids = {
        getattr(getattr(fav, 'recipe', None), 'id', None)
        for fav in getattr(user, 'favourite_recipes', [])
    }
    for r in recipes:
        rid = getattr(r, 'id', None)
        setattr(r, 'is_favourite', rid in fav_recipe_ids)


def get_favourites(repo: AbstractRepository) -> List[Recipe]:
    user = _require_user()
    recipes = [getattr(fav, 'recipe') for fav in getattr(user, 'favourite_recipes', [])]
    recipes = [r for r in recipes if r is not None]
    if not recipes:
        raise NonExistentRecipeException("No favourites yet.")
    return recipes


def search_favourites(filter_by: str, query: str, repo: AbstractRepository) -> List[Recipe]:
    base = get_favourites(repo)
    query = (query or "").lower()
    filtered: List[Recipe] = []
    for recipe in base:
        if filter_by == "name" and query in (getattr(recipe, "name", "") or "").lower():
            filtered.append(recipe)
        elif filter_by == "category":
            category_name = getattr(getattr(recipe, "category", None), "name", "") or ""
            if query in category_name.lower():
                filtered.append(recipe)
        elif filter_by == "author":
            author_name = getattr(getattr(recipe, "author", None), "name", "") or ""
            if query in author_name.lower():
                filtered.append(recipe)
        elif filter_by == "ingredient":
            ingredients = getattr(recipe, "ingredients", []) or []
            if any(query in (ing or "").lower() for ing in ingredients):
                filtered.append(recipe)
    if not filtered:
        raise NonExistentRecipeException(f"No favourites found for {filter_by} containing '{query}'.")
    return filtered

def toggle_favourite(recipe_id: int, repo: AbstractRepository) -> bool:
    """Toggle favourite for recipe_id. Return True if now favourited, False if removed or on error."""
    try:
        user = _require_user()
    except UnknownUserException:
        return False

    if repo is None:
        return False

    recipe = None
    try:
        recipe = repo.get_recipe_by_id(recipe_id)
    except Exception:
        recipe = None

    if not recipe:
        return False

    try:
        if repo.is_recipe_in_favourites(user.username, recipe_id):
            repo.remove_favourite(user, recipe)
            return False
        else:
            repo.add_favourite(user, recipe)
            return True
    except Exception:
        return False

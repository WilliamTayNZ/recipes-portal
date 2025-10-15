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

    # Choose repository call based on filter
    recipes = []
    try:
        if filter_by == 'name':
            if hasattr(repo, 'get_recipes_by_name_paginated'):
                recipes = repo.get_recipes_by_name_paginated(query, page, per_page)
            else:
                all_matches = repo.get_recipes_by_name(query)
                start = (page - 1) * per_page
                end = start + per_page
                recipes = all_matches[start:end]
        elif filter_by == 'author':
            # Prefer repo paginated search when available
            if hasattr(repo, 'get_recipes_by_author_name_paginated'):
                recipes = repo.get_recipes_by_author_name_paginated(query, page, per_page)
            else:
                # Repo-agnostic fallback: filter all recipes by author substring (case-insensitive)
                all_recipes = repo.get_recipes()
                matches = [r for r in all_recipes if query in ((getattr(getattr(r, 'author', None), 'name', '') or '').lower())]
                start = (page - 1) * per_page
                end = start + per_page
                recipes = matches[start:end]
        elif filter_by == 'category':
            if hasattr(repo, 'get_recipes_by_category_name_paginated'):
                recipes = repo.get_recipes_by_category_name_paginated(query, page, per_page)
            else:
                # Repo-agnostic fallback: filter all recipes by category substring (case-insensitive)
                all_recipes = repo.get_recipes()
                matches = [r for r in all_recipes if query in ((getattr(getattr(r, 'category', None), 'name', '') or '').lower())]
                start = (page - 1) * per_page
                end = start + per_page
                recipes = matches[start:end]
        elif filter_by == 'ingredient':
            # Prefer DB paginated ingredient search if available
            if hasattr(repo, 'get_recipes_by_ingredient_name_paginated'):
                recipes = repo.get_recipes_by_ingredient_name_paginated(query, page, per_page)
            else:
                # Fallback: filter all recipes by ingredient substring (case-insensitive)
                all_recipes = repo.get_recipes()
                def _has_ing(r):
                    ings = getattr(r, 'ingredients', []) or []
                    return any(query in ((ing or '').lower()) for ing in ings)
                matches = [r for r in all_recipes if _has_ing(r)]
                start = (page - 1) * per_page
                end = start + per_page
                recipes = matches[start:end]
        else:
            # default to name search
            recipes = repo.get_recipes_by_name_paginated(query, page, per_page)
    except Exception:
        recipes = []

    if not recipes:
        raise NonExistentRecipeException(f"No recipes found for {filter_by} containing '{query}'.")
    return recipes


def count_search_results(filter_by: str, query: str, repo: AbstractRepository) -> int:
    """Count matching recipes for a given filter and query.

    This will use repository-specific fast count methods when available (e.g. count_recipes_by_name),
    otherwise it falls back to loading matches and counting them.
    """
    query = (query or "").lower()
    try:
        if filter_by == 'name' and hasattr(repo, 'count_recipes_by_name'):
            return repo.count_recipes_by_name(query)
        elif filter_by == 'author' and hasattr(repo, 'count_recipes_by_author_name'):
            return repo.count_recipes_by_author_name(query)
        elif filter_by == 'category' and hasattr(repo, 'count_recipes_by_category_name'):
            return repo.count_recipes_by_category_name(query)
        elif filter_by == 'ingredient' and hasattr(repo, 'count_recipes_by_ingredient_name'):
            return repo.count_recipes_by_ingredient_name(query)
        else:
            # Fallback: compute via in-Python filtering over all recipes
            all_recipes = repo.get_recipes()
            if filter_by == 'name':
                matches = [r for r in all_recipes if query in ((getattr(r, 'name', '') or '').lower())]
            elif filter_by == 'author':
                matches = [r for r in all_recipes if query in ((getattr(getattr(r, 'author', None), 'name', '') or '').lower())]
            elif filter_by == 'category':
                matches = [r for r in all_recipes if query in ((getattr(getattr(r, 'category', None), 'name', '') or '').lower())]
            elif filter_by == 'ingredient':
                matches = [r for r in all_recipes if any(query in ((ing or '').lower()) for ing in (getattr(r, 'ingredients', []) or []))]
            else:
                matches = [r for r in all_recipes if query in ((getattr(r, 'name', '') or '').lower())]
            return len(matches)
    except Exception:
        return 0

def count_recipes(repo: AbstractRepository):
    """Get total recipe count"""
    return repo.count_recipes()

def count_recipes_by_name(name: str, repo: AbstractRepository):
    """Get count of recipes matching name"""
    return repo.count_recipes_by_name(name)

def search_recipes(filter_by: str, query: str, repo: AbstractRepository):
    query = query.lower()

    # Use existing function to get all recipes by passing empty string
    all_recipes = repo.get_recipes()

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

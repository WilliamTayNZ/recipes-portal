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


def toggle_favourite(recipe_id: int, repo: AbstractRepository) -> None:
    user = _require_user()
    recipe = repo.get_recipe_by_id(recipe_id)
    if recipe is None:
        raise NonExistentRecipeException(f"Recipe with id {recipe_id} does not exist.")

    favs: List[Favourite] = getattr(user, 'favourite_recipes', [])
    
    # Check if this recipe is already favorited by comparing recipe IDs
    for existing in list(favs):
        existing_recipe = getattr(existing, 'recipe', None)
        if existing_recipe and getattr(existing_recipe, 'id', None) == recipe_id:
            user.remove_favourite_recipe(existing)
            return
    
    # If not found, add it
    identifier = _current_user_identifier()
    target = Favourite(user_id=identifier, user=user, recipe=recipe)
    user.add_favourite_recipe(target)
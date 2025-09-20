from recipe.adapters.repository import AbstractRepository

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
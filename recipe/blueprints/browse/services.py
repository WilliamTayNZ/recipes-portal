from recipe.adapters.repository import AbstractRepository

class NonExistentRecipeException(Exception):
    pass

class UnknownUserException(Exception):
    pass

def get_recipe(recipe_id: int, repo: AbstractRepository):
    recipe = repo.get_recipe(recipe_id)
    if recipe is None:
        raise NonExistentRecipeException(f"Recipe with id {recipe_id} does not exist.")
    return recipe

def get_recipes_by_name(name: str, repo: AbstractRepository):
    recipes = repo.get_recipes_by_name(name)
    if not recipes:
        raise NonExistentRecipeException(f"No recipes found with name containing '{name}'.")
    return recipes
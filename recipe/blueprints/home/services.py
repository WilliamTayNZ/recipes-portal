import recipe.adapters.repository as repo
import random

def get_featured_recipes():
    recipes = repo.repo_instance.get_recipes() if repo.repo_instance else []
    featured = random.sample(recipes, k=min(2, len(recipes))) if recipes else []
    return featured

import recipe.adapters.repository as repo

def get_featured_recipes():
    return repo.repo_instance.get_featured_recipes(2) if repo.repo_instance else []

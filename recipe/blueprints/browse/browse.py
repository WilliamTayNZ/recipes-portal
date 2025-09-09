from flask import Flask, render_template, Blueprint, request
import recipe.blueprints.browse.services as services
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author

import recipe.adapters.repository as repo

recipes_blueprint = Blueprint('recipes_bp', __name__)
browse_blueprint = Blueprint('browse_bp', __name__)

@browse_blueprint.route('/browse', methods=['GET'])
def browse():
    recipes_per_page = 9

    cursor = request.args.get('cursor')

    if cursor is None:
        cursor = 0
    else:
        cursor = int(cursor)

    end = cursor + recipes_per_page

    filter_by = request.args.get('filter_by')
    query = request.args.get('query', '').strip()

    try:
        if filter_by and query:
            recipes = services.search_recipes(filter_by, query, repo.repo_instance)
        else:
            recipes = services.get_recipes_by_name("", repo.repo_instance)
    except services.NonExistentRecipeException:
        recipes = []
    page_recipes = recipes[cursor:end]
    first_recipe_url = None
    last_recipe_url = None
    next_recipe_url = None
    prev_recipe_url = None

    # Preserve search params in pagination links
    extra_params = ""
    if filter_by and query:
        extra_params = f"&filter_by={filter_by}&query={query}"

    if cursor > 0:
        prev_start = max(0, cursor - recipes_per_page)
        prev_recipe_url = f"/browse?cursor={prev_start}{extra_params}"
        first_recipe_url = f"/browse?cursor=0{extra_params}"

    if end < len(recipes):
        last_cursor = ((len(recipes) - 1) // recipes_per_page) * recipes_per_page
        last_recipe_url = f"/browse?cursor={last_cursor}{extra_params}"
        next_recipe_url = f"/browse?cursor={end}{extra_params}"

    return render_template('browse.html', recipes=page_recipes, first_recipe_url=first_recipe_url, last_recipe_url=last_recipe_url, next_recipe_url=next_recipe_url, prev_recipe_url=prev_recipe_url, filter_by=filter_by, query=query)



@recipes_blueprint.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = services.get_recipe(recipe_id, repo.repo_instance)
    return render_template('recipe.html', recipe=recipe)
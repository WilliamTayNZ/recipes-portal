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


    recipes = services.get_recipes_by_name("", repo.repo_instance)
    page_recipes = recipes[cursor:end]
    first_recipe_url = None
    last_recipe_url = None
    next_recipe_url = None
    prev_recipe_url = None

    if cursor > 0:
        prev_start = max(0, cursor - recipes_per_page)
        prev_recipe_url = f"/browse?cursor={prev_start}"
        first_recipe_url = "/browse?cursor=0"

    if end < len(recipes):
        last_recipe_url = f"/browse?cursor={((len(recipes) - 1) // recipes_per_page) * recipes_per_page}"
        next_recipe_url = f"/browse?cursor={end}"

    return render_template('browse.html', recipes=page_recipes, first_recipe_url=first_recipe_url, last_recipe_url=last_recipe_url, next_recipe_url=next_recipe_url, prev_recipe_url=prev_recipe_url)



@recipes_blueprint.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = services.get_recipe(recipe_id, repo.repo_instance)
    return render_template('recipe.html', recipe=recipe)
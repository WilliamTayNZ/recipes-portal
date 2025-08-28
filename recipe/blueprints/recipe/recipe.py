from flask import Blueprint, render_template, abort
import recipe.adapters.repository as repo

recipe_blueprint = Blueprint('recipe_bp', __name__)

@recipe_blueprint.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe(recipe_id):
    # Get the recipe from the repository
    recipe_obj = repo.repo_instance.get_recipe(recipe_id)
    
    if recipe_obj is None:
        abort(404)  # Recipe not found
    
    return render_template('recipe.html', recipe=recipe_obj)

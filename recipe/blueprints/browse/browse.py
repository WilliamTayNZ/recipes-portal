from flask import Flask, render_template, Blueprint, request
from flask_login import login_required
import recipe.blueprints.browse.services as services
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from flask_login import current_user

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

    services.annotate_is_favourite(recipes, repo.repo_instance)
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

    return render_template(
        'browse.html',
        recipes=page_recipes,
        first_recipe_url=first_recipe_url,
        last_recipe_url=last_recipe_url,
        next_recipe_url=next_recipe_url,
        prev_recipe_url=prev_recipe_url,
        filter_by=filter_by,
        query=query,
        mode="browse"
    )



@recipes_blueprint.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = services.get_recipe(recipe_id, repo.repo_instance)
    services.annotate_is_favourite([recipe], repo.repo_instance)
    return render_template('recipe.html', recipe=recipe)


from flask import redirect, url_for

def _render_list(recipes, filter_by=None, query=""):
    recipes_per_page = 9
    cursor = request.args.get('cursor')
    cursor = 0 if cursor is None else int(cursor)
    end = cursor + recipes_per_page
    page_recipes = recipes[cursor:end]

    mode = "favourites" if request.path.startswith("/favourites") else "browse"

    first_recipe_url = None
    last_recipe_url = None
    next_recipe_url = None
    prev_recipe_url = None

    extra_params = ""
    if filter_by and query:
        extra_params = f"&filter_by={filter_by}&query={query}"

    base = f"/{mode}"
    if cursor > 0:
        prev_start = max(0, cursor - recipes_per_page)
        prev_recipe_url = f"{base}?cursor={prev_start}{extra_params}"
        first_recipe_url = f"{base}?cursor=0{extra_params}"

    if end < len(recipes):
        last_cursor = ((len(recipes) - 1) // recipes_per_page) * recipes_per_page
        last_recipe_url = f"{base}?cursor={last_cursor}{extra_params}"
        next_recipe_url = f"{base}?cursor={end}{extra_params}"

    return render_template(
        'browse.html',
        recipes=page_recipes,
        first_recipe_url=first_recipe_url,
        last_recipe_url=last_recipe_url,
        next_recipe_url=next_recipe_url,
        prev_recipe_url=prev_recipe_url,
        filter_by=filter_by,
        query=query,
        mode=mode
    )

@browse_blueprint.route('/favourites', methods=['GET'])
@login_required
def favourites():
    filter_by = request.args.get('filter_by')
    query = request.args.get('query', '').strip()
    try:
        if filter_by and query:
            recipes = services.search_favourites(filter_by, query, repo.repo_instance)
        else:
            recipes = services.get_favourites(repo.repo_instance)
    except services.NonExistentRecipeException:
        recipes = []
    services.annotate_is_favourite(recipes, repo.repo_instance)
    return _render_list(recipes, filter_by=filter_by, query=query)

@browse_blueprint.route('/favourites/<int:recipe_id>/toggle', methods=['POST'])
@login_required
def toggle_favourite(recipe_id):
    services.toggle_favourite(recipe_id, repo.repo_instance)
    ref = request.referrer or url_for('browse_bp.favourites')
    return redirect(ref)
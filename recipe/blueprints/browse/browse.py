from flask import render_template, Blueprint, request, redirect, url_for
from flask_login import login_required
import recipe.blueprints.browse.services as services

import recipe.adapters.repository as repo

recipes_blueprint = Blueprint('recipes_bp', __name__)
browse_blueprint = Blueprint('browse_bp', __name__)

@browse_blueprint.route('/browse', methods=['GET'])
def browse():
    recipes_per_page = 9

    # Get page number from URL parameter
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

    filter_by = request.args.get('filter_by')
    query = request.args.get('query', '').strip()

    try:
        if filter_by and query:
            # Use paginated search
            recipes = services.search_recipes_paginated(filter_by, query, page, recipes_per_page, repo.repo_instance)
            # Use new count helper that handles name/author/category
            total_recipes = services.count_search_results(filter_by, query, repo.repo_instance)
        else:
            # Use paginated browse
            recipes = services.get_recipes_paginated(page, recipes_per_page, repo.repo_instance)
            total_recipes = services.count_recipes(repo.repo_instance)
    except services.NonExistentRecipeException:
        recipes = []
        total_recipes = 0

    services.annotate_is_favourite(recipes, repo.repo_instance)
    
    # Calculate pagination info
    total_pages = (total_recipes + recipes_per_page - 1) // recipes_per_page  # Ceiling division
    first_recipe_url = None
    last_recipe_url = None
    next_recipe_url = None
    prev_recipe_url = None

    # Preserve search params in pagination links
    extra_params = ""
    if filter_by and query:
        extra_params = f"&filter_by={filter_by}&query={query}"

    if page > 1:
        prev_recipe_url = f"/browse?page={page-1}{extra_params}"
        first_recipe_url = f"/browse?page=1{extra_params}"

    if page < total_pages:
        next_recipe_url = f"/browse?page={page+1}{extra_params}"
        last_recipe_url = f"/browse?page={total_pages}{extra_params}"

    return render_template(
        'browse.html',
        recipes=recipes,
        first_recipe_url=first_recipe_url,
        last_recipe_url=last_recipe_url,
        next_recipe_url=next_recipe_url,
        prev_recipe_url=prev_recipe_url,
        filter_by=filter_by,
        query=query,
        mode="browse",
        current_page=page,
        total_pages=total_pages
    )

@recipes_blueprint.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = services.get_recipe(recipe_id, repo.repo_instance)
    services.annotate_is_favourite([recipe], repo.repo_instance)
    return render_template('recipe.html', recipe=recipe)

@browse_blueprint.route('/recipe/<int:recipe_id>/toggle-favourite', methods=['POST'])
@login_required
def toggle_favourite_recipe(recipe_id):
    services.toggle_favourite(recipe_id, repo.repo_instance)

    # Prefer explicit next value from the form (set in templates) so we can include a fragment
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)

    # Fallback to referrer (strip and append fragment) or browse
    ref = request.referrer
    if not ref:
        return redirect(url_for('browse_bp.browse'))

    try:
        base = ref.split('#')[0]
        new_url = f"{base}#card-{recipe_id}"
        return redirect(new_url)
    except Exception:
        return redirect(ref)


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

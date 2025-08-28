from flask import Blueprint, render_template, url_for
import random
import recipe.adapters.repository as repo

home_blueprint = Blueprint('home_bp', __name__)

@home_blueprint.route('/', methods=['GET'])
def home():
    recipes = repo.repo_instance.get_recipes() if repo.repo_instance else []
    featured = random.sample(recipes, k=min(2, len(recipes))) if recipes else []
    return render_template('index.html', featured_recipes=featured)
from flask import Blueprint, render_template, url_for
import random
import recipe.adapters.repository as repo

home_blueprint = Blueprint('home_bp', __name__)

@home_blueprint.route('/', methods=['GET'])
def home():
    featured = repo.repo_instance.get_featured_recipes(2) if repo.repo_instance else []
    return render_template('index.html', featured_recipes=featured)
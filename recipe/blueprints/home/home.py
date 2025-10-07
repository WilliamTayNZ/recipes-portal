from flask import Blueprint, render_template, url_for

import recipe.blueprints.home.services as services

home_blueprint = Blueprint('home_bp', __name__)

@home_blueprint.route('/', methods=['GET'])
def home():
    featured = services.get_featured_recipes()
    return render_template('index.html', featured_recipes=featured)
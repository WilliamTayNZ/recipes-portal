"""Initialize Flask app."""
from datetime import datetime

from pathlib import Path
from flask import Flask, render_template

from recipe.blueprints.home.home import home_blueprint

from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author

import recipe.adapters.repository as repo
from recipe.adapters.memory_repository import MemoryRepository, populate

def create_app():
    app = Flask(__name__)

    data_path = Path('recipe') / 'adapters' / 'data'

    repo.repo_instance = MemoryRepository()
    populate(data_path, repo.repo_instance)

    with app.app_context():
        # Register blueprints.
        from .blueprints.home.home import home_blueprint
        app.register_blueprint(home_blueprint)

        from .blueprints.browse.browse import browse_blueprint
        app.register_blueprint(browse_blueprint)

    return app

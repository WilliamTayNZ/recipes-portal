from flask import Flask
import recipe.adapters.repository as repo
from recipe.adapters.memory_repository import MemoryRepository, populate
from recipe.adapters.datareader.csvdatareader import CSVDataReader


def create_app():
    app = Flask(__name__)

    repo.repo_instance = MemoryRepository()
    populate(repo.repo_instance)

    from .blueprints.home.home import home_blueprint
    from .blueprints.browse.browse import browse_blueprint
    from .blueprints.browse.browse import recipes_blueprint

    app.register_blueprint(home_blueprint)
    app.register_blueprint(browse_blueprint)
    app.register_blueprint(recipes_blueprint)

    return app
from flask import Flask
import recipe.adapters.repository as repo
from recipe.adapters.memory_repository import MemoryRepository, populate
from recipe.adapters.datareader.csvdatareader import CSVDataReader

csv_path = "recipe/adapters/data/recipes.csv"
reader = CSVDataReader(csv_path)
reader.csv_read()


def create_app():
    app = Flask(__name__)

    repo.repo_instance = MemoryRepository()
    populate(repo.repo_instance)

    from .blueprints.home.home import home_blueprint
    from .blueprints.browse.browse import browse_blueprint

    app.register_blueprint(home_blueprint)
    app.register_blueprint(browse_blueprint)

    return app
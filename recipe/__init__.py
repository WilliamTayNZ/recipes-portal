from pathlib import Path

from flask import Flask
import recipe.adapters.repository as repo
from recipe.adapters.memory_repository import MemoryRepository, populate
from recipe.adapters.datareader.csvdatareader import CSVDataReader


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object('config.Config')
    data_path = Path('recipe') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    repo.repo_instance = MemoryRepository()
    populate(data_path, repo.repo_instance)

    # Build the application - these steps require an application context.
    with app.app_context():
        from .blueprints.home.home import home_blueprint
        app.register_blueprint(home_blueprint)

        from .blueprints.browse.browse import browse_blueprint
        app.register_blueprint(browse_blueprint)

        from .blueprints.recipe.recipe import recipe_blueprint
        app.register_blueprint(recipe_blueprint)

        from .blueprints.browse.browse import recipes_blueprint
        app.register_blueprint(recipes_blueprint)

    return app
from pathlib import Path

from flask import Flask, session
from flask_login import LoginManager

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool

import recipe.adapters.repository as repo
from recipe.adapters.memory_repository import MemoryRepository
from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.adapters.orm import mapper_registry, map_model_to_tables

from recipe.adapters.memory_repository import populate
from recipe.adapters.datareader.csvdatareader import CSVDataReader


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object('config.Config')
    data_path = Path('recipe') / 'adapters' / 'data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = Path(app.config['TEST_DATA_PATH'])

    if app.config['REPOSITORY'] == 'memory':
        repo.repo_instance = MemoryRepository()
        populate(data_path, repo.repo_instance)
    elif app.config['REPOSITORY'] == 'database':
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']

        database_echo = app.config['SQLALCHEMY_ECHO']
        database_engine = create_engine(database_uri,
                                        connect_args={"check_same_thread": False},
                                        poolclass=NullPool,
                                        echo=database_echo)

        session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
        repo.repo_instance = SqlAlchemyRepository(session_factory)

        if app.config['TESTING'] == 'True' or len(inspect(database_engine).get_table_names()) == 0:
            print("REPOPULATING DATABASE...")
            clear_mappers()
            mapper_registry.metadata.create_all(database_engine)
            for table in reversed(mapper_registry.metadata.sorted_tables):
                with database_engine.connect() as conn:
                    conn.execute(table.delete())

            map_model_to_tables()

            repo.repo_instance = MemoryRepository()
            populate(data_path, repo.repo_instance)
            print("REPOPULATING DATABASE...")
        else:
            map_model_to_tables()

    # Build the application - these steps require an application context.
    with app.app_context():
        login_manager = LoginManager()
        login_manager.login_view = 'authentication_bp.login'
        login_manager.init_app(app)

        class AuthUserAdapter:
            def __init__(self, user):
                self._user = user

            # Flask-Login API
            @property
            def is_authenticated(self):
                return True

            @property
            def is_active(self):
                return True

            @property
            def is_anonymous(self):
                return False

            def get_id(self):
                return getattr(self._user, 'username')

            # Delegate attributes to domain user
            def __getattr__(self, item):
                return getattr(self._user, item)

        def _wrap(user):
            return AuthUserAdapter(user) if user is not None else None

        @login_manager.user_loader
        def load_user(user_id: str):
            user = repo.repo_instance.get_user(user_id)
            return _wrap(user)

        @login_manager.request_loader
        def load_user_from_request(request):
            username = session.get('user_name')
            if not username:
                return None
            user = repo.repo_instance.get_user(username)
            return _wrap(user)

        from .blueprints.home.home import home_blueprint
        app.register_blueprint(home_blueprint)

        from .blueprints.browse.browse import browse_blueprint
        app.register_blueprint(browse_blueprint)

        from .blueprints.recipe.recipe import recipe_blueprint
        app.register_blueprint(recipe_blueprint)

        from .blueprints.browse.browse import recipes_blueprint
        app.register_blueprint(recipes_blueprint)

        from .blueprints.authentication.authentication import authentication_blueprint
        app.register_blueprint(authentication_blueprint)

    return app
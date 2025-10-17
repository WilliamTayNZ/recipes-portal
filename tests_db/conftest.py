import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers, scoped_session

from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.adapters import repository_populate
from recipe.adapters.orm import mapper_registry, map_model_to_tables
from recipe.adapters.database_repository import SqlAlchemyRepository

from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent.parent
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATA_PATH = PROJECT_ROOT / "recipe" / "adapters" / "data"

TEST_DATA_PATH_DATABASE_FULL = get_project_root() / "tests" / "data"
TEST_DATA_PATH_DATABASE_LIMITED = get_project_root() / "tests" / "data"

TEST_DATABASE_URI_FILE = 'sqlite:///recipe-test.db'
TEST_DATABASE_URI_IN_MEMORY = "sqlite://"

@pytest.fixture
def database_engine():
    clear_mappers()

    engine = create_engine(TEST_DATABASE_URI_FILE)
    mapper_registry.metadata.create_all(engine)  # conditionally create database tables
    with engine.begin() as connection:
        for table in reversed(mapper_registry.metadata.sorted_tables):
            connection.execute(table.delete())
    map_model_to_tables()

    # create the database session factory using sessionmaker (this has to be done once, in a global manner)
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    # create the SQLAlchemy DatabaseRepository instance for an sqlite3-based repository
    repo_instance = SqlAlchemyRepository(session_factory)
    database_mode = True
    # Use LIMITED test data for database_engine fixture so tests pass
    repository_populate.populate(TEST_DATA_PATH_DATABASE_LIMITED, repo_instance, database_mode)

    yield engine
    mapper_registry.metadata.drop_all(engine)

# Fixture for a fresh session factory
@pytest.fixture
def session_factory():
    clear_mappers()
    from sqlalchemy import create_engine

    engine = create_engine(TEST_DATABASE_URI_IN_MEMORY)
    map_model_to_tables()
    mapper_registry.metadata.create_all(engine)

    # Clear tables
    with engine.begin() as conn:
        for table in reversed(mapper_registry.metadata.sorted_tables):
            conn.execute(table.delete())

    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    # Populate the database with test data
    repo_instance = SqlAlchemyRepository(session_factory)
    database_mode = True
    repository_populate.populate(TEST_DATA_PATH_DATABASE_FULL, repo_instance, database_mode)

    yield session_factory

    mapper_registry.metadata.drop_all(engine)
    clear_mappers()

# Fixture for a repository instance
@pytest.fixture
def repo(session_factory):
    return SqlAlchemyRepository(session_factory)

# Fixture for an empty in-memory session (optional)
@pytest.fixture
def empty_session():
    clear_mappers()
    engine = create_engine("sqlite://")
    map_model_to_tables()
    mapper_registry.metadata.create_all(engine)

    with engine.begin() as conn:
        for table in reversed(mapper_registry.metadata.sorted_tables):
            conn.execute(table.delete())

    session = scoped_session(sessionmaker(bind=engine))
    yield session
    session.close()
    mapper_registry.metadata.drop_all(engine)
    clear_mappers()

import pytest

from recipe.adapters.database_repository import SqlAlchemyRepository
from recipe.domainmodel.user import User

def make_repo(session_factory) -> SqlAlchemyRepository:
    return SqlAlchemyRepository(session_factory)



def test_repo_can_add_user(session_factory):
    repo = make_repo(session_factory)

    user = User('Dave', 'EasyPassword123')
    repo.add_user(user)

    user2 = repo.get_user('Dave')

    assert user2 == user


def test_repository_can_retrieve_a_user(session_factory):
    repo = make_repo(session_factory)

    user = repo.get_user('fmercury')

    assert user.username == 'fmercury'
    assert user.check_password('mvNNbc1eLA$i')

def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = make_repo(session_factory)
    user = repo.get_user('thisisanonexistentuserwhichwillneverbemade123')
    assert user is None

# py -m pytest -v tests_db/unit/test_authentication_db_repo.py
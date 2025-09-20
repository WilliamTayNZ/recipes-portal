# For fixtures shared by multiple test files, pytest automatically loads themm

import pytest

from recipe import create_app
from recipe.adapters.memory_repository import MemoryRepository, populate

from utils import get_project_root

# DATA_PATH = get_project_root() / "recipe" / "adapters" / "data"
TEST_DATA_PATH = get_project_root() / "tests" / "data"

# the data in TEST_DATA_PATH is IDENTICAL to the original DATA_PATH
# This is to make sure our tests work with our actual data, which is very large
# For example, we need to test that pagination limits the number of recipes on the Browse page 
# We cannot do this with a small recipes.csv data set
# Hence, we just use the original one

@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    populate(TEST_DATA_PATH, repo)

    return repo

@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,                                # Set to True during testing.
        'TEST_DATA_PATH': TEST_DATA_PATH,               # Path for loading test data into the repository.
        'WTF_CSRF_ENABLED': False                       # test_client will not send a CSRF token, so disable validation.
    })

    return my_app.test_client()


class AuthenticationManager:
    def __init__(self, client):
        self.__client = client

    def login(self, user_name='thorke', password='cLQ^C#oFXloS'):
        return self.__client.post(
            'authentication/login',
            data={'user_name': user_name, 'password': password}
        )

    def logout(self):
        return self.__client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)
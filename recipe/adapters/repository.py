import abc
from typing import List
from datetime import date

from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.user import User

repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        print(f'RepositoryException: {message}')


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_recipe(self, recipe: Recipe):
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipe_by_id(self, recipe_id: int):
        """Return a single Recipe by id"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_recipe(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_first_recipe(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_recipe(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes(self) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes_by_id(self, id_list: List[int]) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_author(self, author: Author):
        raise NotImplementedError

    @abc.abstractmethod
    def get_authors_by_name(self, author_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes_by_author_name(self, author_name: str) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_category(self, category: Category):
        raise NotImplementedError

    @abc.abstractmethod
    def get_category_by_name(self, category_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes_by_category_name(self, category_name: str) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes_by_name(self, name: str) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_favourite(self, user: User, recipe: Recipe):
        """Add a recipe to user's favorites"""
        raise NotImplementedError

    @abc.abstractmethod
    def remove_favourite(self, user: User, recipe: Recipe):
        """Remove a recipe from user's favorites"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_user_favourites(self, username: str) -> List[Recipe]:
        """Get all favorite recipes for a user"""
        raise NotImplementedError

    @abc.abstractmethod
    def is_recipe_in_favourites(self, username: str, recipe_id: int) -> bool:
        """Check if a recipe is in user's favorites"""
        raise NotImplementedError

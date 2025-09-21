import abc
from typing import List
from datetime import date

from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category

repo_instance = None


class RepositoryException(Exception):

    def __init__(self, message=None):
        print(f'RepositoryException: {message}')


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_recipe(self, recipe: Recipe):
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipe_by_id(self) -> List[Recipe]:
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
    def get_author_by_name(self, author_name: str):
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
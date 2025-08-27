import abc
from typing import List
from datetime import date

from recipe.domainmodel.user import User
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe

repo_instance = None

class RepositoryException(Exception):
    def __init__(self, message=None):
        pass

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_recipe(self, recipe: Recipe) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipe_by_id(self, recipe_id: int) -> Recipe | None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes(self) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_recipes(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def add_author(self, author: Author) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_author_by_id(self, author_id: int) -> Author:
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes_by_author(self, author_id: int) -> List[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_category(self, category: Category) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_category_by_id(self, category_id: int) -> Category:
        raise NotImplementedError

    @abc.abstractmethod
    def get_recipes_by_category(self, category_id: int) -> List[Recipe]:
        raise NotImplementedError
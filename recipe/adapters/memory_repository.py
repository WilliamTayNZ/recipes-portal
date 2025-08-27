from typing import List

from pathlib import Path
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.adapters.repository import AbstractRepository, RepositoryException

class MemoryRepository(AbstractRepository):
    def __init__(self):
        self.__recipes: List[Recipe] = []
        self.__recipes_index = {}  # id -> Recipe
        self.__authors = {}  # id -> Author
        self.__categories = {}  # id -> Category

    def add_recipe(self, recipe: Recipe):
        """
        Add a Recipe to the repository.
        """
        if not isinstance(recipe, Recipe):
            raise TypeError("Expected a Recipe instance")

        recipe_id = recipe.id

        if recipe_id is None: # Currently not necessary cuz Recipe class ensures valid ID
            raise RepositoryException("Recipe has no id attribute")
        if recipe_id in self.__recipes_index:
            raise RepositoryException(f"Duplicate recipe id: {recipe_id}")

        self.__recipes_index[recipe_id] = recipe
        self.__recipes.append(recipe)

        # Link with Author class
        author = recipe.author

        if author:
            existing_author = self.__authors.get(author.id)
            if existing_author is None:
                self.__authors[author.id] = author
                existing_author = author
            if recipe not in existing_author.recipes:
                try:
                    existing_author.add_recipe(recipe)
                except ValueError:
                    pass

        # Link with Category class
        category = recipe.category

        if category:
            existing_category = self.__categories.get(category.id)
            if existing_category is None:
                self.__categories[category.id] = category
                existing_category = category
            if recipe not in existing_category.recipes:
                try:
                    existing_category.add_recipe(recipe)
                except ValueError:
                    pass

    def get_recipe_by_id(self, recipe_id: int):
        return self.__recipes_index.get(recipe_id)

    def get_recipes(self) -> List[Recipe]:
        return list(self.__recipes)

    def get_number_of_recipes(self):
        return len(self.__recipes)

    def add_author(self, author: Author):
        if not isinstance(author, Author):
            raise TypeError("Expected an Author instance")

        author_id = author.id

        if author_id is None:
            raise RepositoryException("Author has no ID")
        if author_id in self.__authors:
            raise RepositoryException(f"Duplicate author ID: {author_id}")

        self.__authors[author_id] = author

    def get_author_by_id(self, author_id: int):
        author = self.__authors.get(author_id)
        if author is None:
            raise RepositoryException(f"No author found with id: {author_id}")
        return author

    def get_recipes_by_author(self, author_id: int) -> List[Recipe]:
        author = self.__authors.get(author_id)
        if author is None:
            raise RepositoryException(f"No author found with id: {author_id}")
        return author.recipes

    def add_category(self, category: Category):
        if not isinstance(category, Category):
            raise TypeError("Expected a Category instance")

        category_id = category.id

        if category_id is None:
            raise RepositoryException("Category has no id")
        if category_id in self.__categories:
            raise RepositoryException(f"Duplicate category: {category_id}")

        self.__categories[category_id] = category

    def get_category_by_id(self, category_id: int):
        category = self.__categories.get(category_id)
        if category is None:
            raise RepositoryException(f"No category found with id: {category_id}")
        return category

    def get_recipes_by_category(self, category_id: int) -> List[Recipe]:
        category = self.__categories.get(category_id)
        if category is None:
            raise RepositoryException(f"No category found with id: {category_id}")
        return category.recipes

def populate(data_path: Path, repo: MemoryRepository):
    reader = CSVDataReader(data_path)
    reader.csv_read()

    # Register recipes with the repo (this also links authors & categories)
    for recipe in reader.recipes:
        repo.add_recipe(recipe)
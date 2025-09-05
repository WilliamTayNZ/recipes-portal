from pathlib import Path
from typing import List, Iterable
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.adapters.repository import AbstractRepository, RepositoryException
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category

class MemoryRepository(AbstractRepository):

    def __init__(self):
        self.__recipes: List[Recipe] = []
        self.__recipes_index = dict()  # id -> Recipe
        self.__authors = dict()  # name -> Author
        self.__categories = dict()  # name -> Category

        self.__categories_by_id = dict()  # id -> Category
        self.__authors_by_id = dict()  # id -> Author


    def add_recipe(self, recipe: Recipe):
        if not isinstance(recipe, Recipe):
            raise TypeError("Expected a Recipe instance")
        # support recipe.recipe_id or recipe.id
        recipe_id = getattr(recipe, "recipe_id", None) or getattr(recipe, "id", None)
        if recipe_id is None:
            raise RepositoryException("Recipe has no id attribute")
        if recipe_id in self.__recipes_index:
            raise RepositoryException(f"Duplicate recipe_id: {recipe_id}")
            #return  # ignore duplicates
        self.__recipes_index[recipe_id] = recipe
        self.__recipes.append(recipe)

    def get_recipe(self, recipe_id: int):
        return self.__recipes_index.get(recipe_id)

    def get_recipes(self) -> List[Recipe]:
        return list(self.__recipes)

    def get_number_of_recipe(self):
        return len(self.__recipes)

    def get_recipes_by_name(self, name: str) -> List[Recipe]:
        name = (name or "").strip().lower()
        def _name_key(r: Recipe):
            return (getattr(r, "name", "") or "").lower()
        if not name:
            return sorted(self.__recipes, key=_name_key)
        matches = [r for r in self.__recipes if name in _name_key(r)]
        return sorted(matches, key=_name_key)

    def get_first_recipe(self):
        return self.__recipes[0] if self.__recipes else None

    def get_last_recipe(self):
        return self.__recipes[-1] if self.__recipes else None

    def get_recipes_by_id(self, id_list: List[int]) -> List[Recipe]:
        return [self.__recipes_index[i] for i in id_list if i in self.__recipes_index]

    def add_author(self, author: Author):
        if not isinstance(author, Author):
            raise TypeError("Expected an Author instance")
        name = getattr(author, "name", None)
        if name is None:
            raise RepositoryException("Author has no author_name")
        if name in self.__authors:
            return
        if author.id in self.__authors:
            raise RepositoryException(f"Author with id: {author.id} already exists")
        self.__authors[author.id] = author

    def get_author(self, author_id: int) -> Author:
        if author_id in self.__authors:
            return self.__authors[author_id]
        if author_id not in self.__authors:
            raise RepositoryException(f"Author with id: {author_id} does not exist")
        return self.__authors.get(author_id)

    #def get_author(self, author_name: str):
        #if author_name not in self.__authors:
            #raise RepositoryException(f"Author with name: {author_name} does not exist")
        #return self.__authors.get(author_name)


    def get_recipes_by_author_id(self, author_id: int) -> List[Recipe]:
        if author_id not in self.__authors:
            raise RepositoryException(f"Author with id: {author_id} does not exist")
        return [r for r in self.__recipes if getattr(getattr(r, "author", None), "id", None) == author_id]

    def get_recipes_by_author(self, author_name: str) -> List[Recipe]:
        #return [r for r in self.__recipes if getattr(getattr(r, "author", None), "author_name", None) == author_name]
        return [r for r in self.__recipes if getattr(getattr(r, "author", None), "name", None) == author_name]

    def add_category(self, category: Category):
        if not isinstance(category, Category):
            raise TypeError("Expected a Category instance")
        if getattr(category, "id", None) is None:
            raise RepositoryException("Category has no id")
        if not getattr(category, "name", None):
            raise RepositoryException("Category has no name")

        if category.id in self.__categories:
            raise RepositoryException(f"Category with id: {category.id} already exists")

        #name = getattr(category, "name", None)
        #if name is None:
            raise RepositoryException("Category has no category_name")
        #if name in self.__categories:
            raise RepositoryException(f"Category with name: {name} already exists")
        self.__categories[category.id] = category

    def get_category(self, category_id: int):
        if category_id not in self.__categories:
            raise RepositoryException(f"Category with id: {category_id} does not exist")
        return self.__categories.get(category_id)

    def get_recipes_by_category(self, category_id: str) -> List[Recipe]:
        if not isinstance(category_id, int):
            raise TypeError("category_id must be an int")
        if category_id not in self.__categories:
            raise RepositoryException(f"Category with id: {category_id} does not exist")
        return [r for r in self.__recipes if getattr(getattr(r, "category", None), "id", None) == category_id]
        #return [r for r in self.__recipes if getattr(getattr(r, "category", None), "category_name", None) == category_name]

def populate(repo: AbstractRepository):
    adapters_dir = Path(__file__).resolve().parent
    csv_path = adapters_dir / "data" / "recipes.csv"

    print(f"[populate] csv_path = {csv_path}")
    print(f"[populate] exists?  {csv_path.exists()}")

    if not csv_path.exists():
        raise RepositoryException(f"CSV file not found: {csv_path}")

    try:
        reader = CSVDataReader(str(csv_path))
        reader.csv_read()

        authors_iter: Iterable[Author] = reader.authors.values() if isinstance(reader.authors,
                                                                               dict) else reader.authors
        for author in authors_iter:
            try:
                repo.add_author(author)
            except Exception:
                pass

        cats_iter: Iterable[Category] = reader.categories.values() if isinstance(reader.categories,
                                                                                 dict) else reader.categories
        for cat in cats_iter:
            try:
                repo.add_category(cat)
            except Exception:
                pass

        for recipe in getattr(reader, "recipes", []):
            try:
                repo.add_recipe(recipe)
            except Exception:
                pass

        print(f"[populate] loaded {repo.get_number_of_recipe()} recipes, "
              f"{len(getattr(repo, '_MemoryRepository__authors', {}))} authors, "
              f"{len(getattr(repo, '_MemoryRepository__categories', {}))} categories")

    except FileNotFoundError as e:
        raise RepositoryException(f"File not found: {e}") from e
    except Exception as e:
        raise RepositoryException(f"Error populating repository: {e}") from e
from pathlib import Path
from typing import List, Iterable
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.adapters.repository import AbstractRepository, RepositoryException
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.user import User

import csv # to read users.csv, for recipes.csv we use the CSVDataReader class
from werkzeug.security import generate_password_hash

class MemoryRepository(AbstractRepository):

    def __init__(self):
        self.__recipes: List[Recipe] = []
        self.__recipes_index = dict()  # id -> Recipe
        self.__categories = dict() # name -> Category
        self.__users = dict() # username -> User
        self.__reviews = dict()  # review_id -> Review

        self.__authors_by_id = dict()  # id -> Author
        self.__categories_by_id = dict() # id -> Category
        self.__authors_by_name = dict() # name -> List(Author)

    
    # User functions
   
    def add_user(self, user: User):
        self.__users[user.username] = user

    def get_user(self, username) -> User:
        if username not in self.__users:
            return None
        return self.__users[username]

    
    # Recipe functions

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
        
        # Update Category and Author objects' recipes list
        recipe.category.add_recipe(recipe)
        recipe.author.add_recipe(recipe) 

    def get_recipe_by_id(self, recipe_id: int):
        return self.__recipes_index.get(recipe_id)

    def get_recipes(self) -> List[Recipe]:
        return list(self.__recipes)

    def get_featured_recipes(self, limit: int = 6) -> List[Recipe]:
        import random
        return random.sample(self.__recipes, k=min(limit, len(self.__recipes))) if self.__recipes else []

    def get_recipes_paginated(self, page: int, per_page: int) -> List[Recipe]:
        """Get a page of recipes using list slicing"""
        start = (page - 1) * per_page
        end = start + per_page
        return self.__recipes[start:end]

    def get_recipes_by_name_paginated(self, name: str, page: int, per_page: int) -> List[Recipe]:
        """Search recipes by name with pagination - filters first, then paginates"""
        matching_recipes = self.get_recipes_by_name(name)
        start = (page - 1) * per_page
        end = start + per_page
        return matching_recipes[start:end]

    def count_recipes(self) -> int:
        """Count total recipes in memory"""
        return len(self.__recipes)

    def count_recipes_by_name(self, name: str) -> int:
        """Count recipes matching name in memory"""
        return len(self.get_recipes_by_name(name))

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


    # Author functions
    def add_author(self, author: Author):
        if not isinstance(author, Author):
            raise TypeError("Expected an Author instance")
        
        author_id = getattr(author, "id", None)
        if author_id is None:
            raise RepositoryException("Author has no id")
        if author_id in self.__authors_by_id:
            raise RepositoryException(f"Author with id: {author_id} already exists")

        self.__authors_by_id[author.id] = author

        author_name = getattr(author, "name", None)
        if author_name is None:
            raise RepositoryException("Author has no name")
        if author_name not in self.__authors_by_name:
            self.__authors_by_name[author.name] = [author]
        else:
            self.__authors_by_name[author.name].append(author)


    def get_authors_by_name(self, name: str) -> Author:
        if name not in self.__authors_by_name:
            raise RepositoryException(f"Author with name: {name} does not exist")
        return self.__authors_by_name[name]

    def get_author_by_id(self, author_id: int) -> Author:
        if author_id not in self.__authors_by_id:
            raise RepositoryException(f"Author with id: {author_id} does not exist")
        return self.__authors_by_id[author_id]
    
    def get_recipes_by_author_id(self, author_id: int) -> List[Recipe]:
        if author_id not in self.__authors_by_id:
            raise RepositoryException(f"Author with id: {author_id} does not exist")
        return [r for r in self.__recipes if getattr(getattr(r, "author", None), "id", None) == author_id]

    def get_recipes_by_author_name(self, author_name: str) -> List[Recipe]:
        #return [r for r in self.__recipes if getattr(getattr(r, "author", None), "author_name", None) == author_name]
        return [r for r in self.__recipes if getattr(getattr(r, "author", None), "name", None) == author_name]

    # Category functions
    def add_category(self, category: Category):
        if not isinstance(category, Category):
            raise TypeError("Expected a Category instance")
        #if getattr(category, "id", None) is None:
        #    raise RepositoryException("Category has no id")
        if not getattr(category, "name", None):
            raise RepositoryException("Category has no name")

        if category.name in self.__categories:
            raise RepositoryException(f"Category with name: {category.name} already exists")

        #name = getattr(category, "name", None)
        #if name is None:
            raise RepositoryException("Category has no category_name")
        #if name in self.__categories:
            raise RepositoryException(f"Category with name: {name} already exists")
        self.__categories[category.name] = category

    def get_category_by_name(self, category_name: str):
        if category_name not in self.__categories:
            raise RepositoryException(f"Category with name: {category_name} does not exist")
        return self.__categories.get(category_name)

    def get_recipes_by_category_name(self, category_name: str) -> List[Recipe]:
        if not isinstance(category_name, str):
            raise TypeError("category_name must be a str")
        if category_name not in self.__categories:
            raise RepositoryException(f"Category with name: {category_name} does not exist")
        return [r for r in self.__recipes if getattr(getattr(r, "category", None), "name", None) == category_name]

    # Review functions
    def add_review(self, review):
        print("Added a review successfully")
        if not hasattr(review, 'recipe') or not hasattr(review, 'user'):
            raise RepositoryException("Review must have recipe and user")
        
        recipe = self.get_recipe_by_id(review.recipe.id)
        if recipe is None:
            raise RepositoryException("Recipe not found")
        
        # Auto-generate ID if not provided (for new reviews)
        if review.id is None:
            # Generate the review ID based on the maximum existing ID to avoid collisions
            # Using len() would cause ID reuse after deletions!
            if self.__reviews:
                max_id = max(self.__reviews.keys())
                review.id = max_id + 1
            else:
                review.id = 1

            # OLD BUGGY VERSION: Using len() causes ID reuse after deletions! 
            # hence test_Review_id_no_colission_after_deletion fails
            # review.id = len(self.__reviews) + 1
            
        recipe.add_review(review)
        review.user.add_review(review)
        self.__reviews[review.id] = review
        
        print("Added a review successfully")

    def delete_review(self, review_id: int, username: str):
        print(f"[DEBUG] Attempting to delete review_id={review_id} by username={username}")
        print(f"[DEBUG] Available review IDs: {list(self.__reviews.keys())}")
        
        review = self.__reviews.get(review_id)

        if review is None:
            print(f"[DEBUG] Review {review_id} not found in repository")
            return False

        print(f"[DEBUG] Review found. Owner: {review.user.username}")
        
        # Check that the user created this review
        if review.user.username != username:
            print(f"[DEBUG] Username mismatch: {review.user.username} != {username}")
            return False

        recipe = review.recipe
        user = review.user
            
        recipe.remove_review(review)
        user.remove_review(review)
        del self.__reviews[review_id]
        
        print(f"[DEBUG] Review {review_id} deleted successfully")
        return True
            

    # Favourite function
    def add_favourite(self, user: User, recipe: Recipe):
        if user is None or recipe is None:
            return
        # create a Favourite domain object and add to user's favourites
        from recipe.domainmodel.favourite import Favourite
        identifier = getattr(user, 'username', None) or getattr(user, 'id', None)
        fav = Favourite(user_id=identifier, user=user, recipe=recipe)
        try:
            user.add_favourite_recipe(fav)
        except Exception:
            # if user.add_favourite_recipe raises (duplicate), ignore
            pass

    def remove_favourite(self, user: User, recipe: Recipe):
        if user is None or recipe is None:
            return
        # find the Favourite object for this recipe and remove it
        fav_to_remove = None
        for fav in list(getattr(user, 'favourite_recipes', [])):
            if getattr(getattr(fav, 'recipe', None), 'id', None) == getattr(recipe, 'id', None):
                fav_to_remove = fav
                break
        if fav_to_remove:
            try:
                user.remove_favourite_recipe(fav_to_remove)
            except Exception:
                pass

    def get_user_favourites(self, username: str) -> List[Recipe]:
        user = self.get_user(username)
        if user is None:
            return []
        return [fav.recipe for fav in user.favourite_recipes if fav.recipe is not None]

    def is_recipe_in_favourites(self, username: str, recipe_id: int) -> bool:
        user = self.get_user(username)
        if user is None:
            return False
        return any(fav.recipe.id == recipe_id for fav in user.favourite_recipes if fav.recipe is not None)

def read_general_csv_file(filename: str): # Used for any csv file that is NOT recipes.csv, which is read with CSVDataReader
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row

def load_recipes(data_path: Path, repo: MemoryRepository):
    csv_path = data_path / "recipes.csv"
    if not csv_path.exists():
        raise RepositoryException(f"CSV file not found: {csv_path}")
    reader = CSVDataReader(str(csv_path))
    reader.csv_read()
    for recipe in getattr(reader, "recipes", []):
        try:
            repo.add_recipe(recipe)
        except Exception:
            pass
    return reader

def load_authors(reader, repo: MemoryRepository):
    authors_iter: Iterable[Author] = reader.authors.values() if isinstance(reader.authors, dict) else reader.authors
    for author in authors_iter:
        try:
            repo.add_author(author)
        except Exception:
            pass

def load_categories(reader, repo: MemoryRepository):
    cats_iter: Iterable[Category] = reader.categories.values() if isinstance(reader.categories, dict) else reader.categories
    for cat in cats_iter:
        try:
            repo.add_category(cat)
        except Exception:
            pass

def load_users(data_path: Path, repo: MemoryRepository):
    users = dict()
    users_filename = str(Path(data_path) / "users.csv")
    for data_row in read_general_csv_file(users_filename):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users

def populate(data_path: Path, repo: MemoryRepository):
    # Load recipes and related data into the repository.
    reader = load_recipes(data_path, repo)
    load_authors(reader, repo)
    load_categories(reader, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # If you have comments/reviews, load them here (implement load_comments if needed)
    # load_comments(data_path, repo, users)

    print(f"[populate] loaded {repo.get_number_of_recipe()} recipes, "
          f"{len(getattr(repo, '_MemoryRepository__authors_by_id', {}))} authors, "
          f"{len(getattr(repo, '_MemoryRepository__categories', {}))} categories,"
          f"{len(getattr(repo, '_MemoryRepository__users', {}))} users",
          )
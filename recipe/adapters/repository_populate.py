from pathlib import Path
from werkzeug.security import generate_password_hash
import csv

from recipe.adapters.repository import AbstractRepository, RepositoryException
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.domainmodel.user import User
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe
from typing import Iterable

def read_general_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        headers = next(reader)
        for row in reader:
            row = [item.strip() for item in row]
            yield row

def load_recipes(data_path: Path, repo, database_mode: bool = False):
    """Load recipes from CSV file"""
    csv_path = data_path / "recipes.csv"
    if not csv_path.exists():
        raise RepositoryException(f"CSV file not found: {csv_path}")
    
    reader = CSVDataReader(str(csv_path))
    reader.csv_read()
    
    # Track unique authors and categories to avoid duplicates for database repo
    authors_added = set()
    categories_added = set()
    
    for recipe in getattr(reader, "recipes", []):
        try:
            if database_mode:
                # For database repository, check for duplicates before adding
                if recipe.author.name not in authors_added:
                    repo.add_author(recipe.author)
                    authors_added.add(recipe.author.name)
                
                if recipe.category.name not in categories_added:
                    repo.add_category(recipe.category)
                    categories_added.add(recipe.category.name)
            
            repo.add_recipe(recipe)
        except Exception as e:
            print(f"Error adding recipe {recipe.id}: {e}")
            continue
    
    return reader

def load_authors(reader, repo, database_mode: bool = False):
    """Load authors from CSV reader"""
    if database_mode:
        # For database repository, authors are already added when recipes are added
        # because the CSV reader creates them and they're added via add_recipe
        pass
    else:
        # For memory repository, add authors separately
        authors_iter: Iterable[Author] = reader.authors.values() if isinstance(reader.authors, dict) else reader.authors
        for author in authors_iter:
            try:
                repo.add_author(author)
            except Exception:
                pass

def load_categories(reader, repo, database_mode: bool = False):
    """Load categories from CSV reader"""
    if database_mode:
        # For database repository, categories are already added when recipes are added
        # because the CSV reader creates them and they're added via add_recipe
        pass
    else:
        # For memory repository, add categories separately
        cats_iter: Iterable[Category] = reader.categories.values() if isinstance(reader.categories, dict) else reader.categories
        for cat in cats_iter:
            try:
                repo.add_category(cat)
            except Exception:
                pass

def load_users(data_path: Path, repo):
    """Load users from CSV file"""
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

def populate(data_path: Path, repo, database_mode: bool = False):
    """Universal populate function that works with both MemoryRepository and SqlAlchemyRepository"""
    # Load recipes and related data into the repository
    reader = load_recipes(data_path, repo, database_mode)
    load_authors(reader, repo, database_mode)
    load_categories(reader, repo, database_mode)
    
    # Load users into the repository
    users = load_users(data_path, repo)
    
    # Print statistics
    if hasattr(repo, '_MemoryRepository__authors_by_id'):
        # Memory repository
        print(f"[populate] loaded {repo.get_number_of_recipe()} recipes, "
              f"{len(getattr(repo, '_MemoryRepository__authors_by_id', {}))} authors, "
              f"{len(getattr(repo, '_MemoryRepository__categories', {}))} categories, "
              f"{len(getattr(repo, '_MemoryRepository__users', {}))} users")
    else:
        # Database repository
        print(f"[populate] loaded {repo.get_number_of_recipe()} recipes")

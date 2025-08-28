from pathlib import Path
import pytest
import csv
from datetime import datetime

from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.nutrition import Nutrition


# Fixtures
@pytest.fixture
def csv_path():
    return Path(__file__).resolve().parent.parent / "data" / "recipes.csv"

@pytest.fixture
def read_csv(csv_path):
    reader = CSVDataReader(csv_path)
    reader.csv_read()
    return reader

def build_csvreader_from_rows(rows, tmp_path):
    """
    Builds a CSVDataReader from rows dict.
    Writes them to a temp CSV under tmp_path.
    Use this to create rows for edge-case unit testing
    """
    fieldnames = list(rows[0].keys())
    csv_file = tmp_path / "test.csv"

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    reader = CSVDataReader(csv_file)
    reader.csv_read()
    return reader


# Tests

def test_reader_creates_domain_objects(read_csv):
    recipes = read_csv.recipes
    authors = read_csv.authors
    categories = read_csv.categories

    # Sanity checks
    assert len(recipes) > 0
    assert all(isinstance(r, Recipe) for r in recipes)
    assert all(isinstance(a, Author) for a in authors)
    assert all(isinstance(c, Category) for c in categories)

    # Relationship check
    for r in recipes:
        assert r.author in authors
        assert r.category in categories
        assert r in r.author.recipes
        assert r in r.category.recipes

def test_recipe_and_nutrition_fields_mapped(read_csv):
    for r in read_csv.recipes:
        assert isinstance(r.id, int)
        assert r.name == r.name.strip()
        assert isinstance(r.servings, str)

        n = r.nutrition
        assert all(isinstance(x, int) for x in [n.calories, n.cholesterol, n.sodium])
        assert all(isinstance(x, float) for x in [n.fat, n.saturated_fat, n.carbohydrates, n.fiber, n.sugar, n.protein])

def test_ingredients_lists_parsed_correctly(read_csv):
    for r in read_csv.recipes:
        assert isinstance(r.ingredient_quantities, list)
        assert isinstance(r.ingredients, list)
        assert isinstance(r.instructions, list)

        assert all(isinstance(x, str) for x in r.ingredient_quantities)
        assert all(isinstance(x, str) for x in r.ingredients)
        assert all(isinstance(x, str) for x in r.instructions)

# Check that each AuthorId in the CSV maps to exactly one Author object instance (no duplicates)
def test_deduplicates_authors_by_id(read_csv):
    # Map: AuthorId -> all Author object identities seen for that AuthorId
    author_objects_by_id = {}
    for recipe in read_csv.recipes:
        author_id = recipe.author.id
        author_objects_by_id.setdefault(author_id, set()).add(id(recipe.author))

    for author_id, object_ids in author_objects_by_id.items():
        assert len(object_ids) == 1, f"ERROR: Author {author_id} has multiple objects"

    # Number of Author objects stored equals the number of unique AuthorIds
    assert len(read_csv.authors) == len(author_objects_by_id)

def test_deduplicates_categories_by_name(read_csv):
    # Map: CategoryName -> all object identities seen for that CategoryName
    category_objects_by_name = {}
    for recipe in read_csv.recipes:
        name = recipe.category.name
        category_objects_by_name.setdefault(name, set()).add(id(recipe.category))

    for name, object_ids in category_objects_by_name.items():
        assert len(object_ids) == 1, f"ERROR: Category '{name}' has multiple objects"

    # Number of Category objects stored equals the number of unique CategoryNames
    assert len(read_csv.categories) == len(category_objects_by_name)


def test_numeric_zeros_parse_correctly(tmp_path):
    row = {
        "RecipeId": "1", "Name": "X", "AuthorId": "1", "AuthorName": "A", "RecipeCategory": "C",
        "CookTime": "0", "PrepTime": "0", "TotalTime": "0", "DatePublished": "1st Jan 2020", "Description": "",
        "Images": "",
        "RecipeIngredientQuantities": "['NA']",
        "RecipeIngredientParts": "['NA']",
        "RecipeInstructions": "['Step 1']",
        "Calories": "0", "FatContent": "0", "SaturatedFatContent": "0",
        "CholesterolContent": "0", "SodiumContent": "0", "CarbohydrateContent": "0",
        "FiberContent": "0", "SugarContent": "0", "ProteinContent": "0",
        "RecipeServings": "4", "RecipeYield": "NA",
    }

    reader = build_csvreader_from_rows([row], tmp_path)
    n = reader.recipes[0].nutrition

    assert n.calories == 0
    assert n.cholesterol == 0
    assert n.sodium == 0
    assert n.fat == 0.0
    assert n.saturated_fat == 0.0
    assert n.carbohydrates == 0.0
    assert n.fiber == 0.0
    assert n.sugar == 0.0
    assert n.protein == 0.0


def test_recipe_yield_none_when_NA(tmp_path):
    row = {
        "RecipeId": "2", "Name": "Y", "AuthorId": "1", "AuthorName": "A", "RecipeCategory": "C",
        "CookTime": "15", "PrepTime": "5", "DatePublished": "9th Aug 2009", "Description": "", "Images": "",
        "RecipeIngredientQuantities": "['1']", "RecipeIngredientParts": "['sugar']", "RecipeInstructions": "['Stir']",
        "RecipeServings": "2", "RecipeYield": "NA",   # missing yield
        "Calories": "10", "FatContent": "1.0", "SaturatedFatContent": "0.5",
        "CholesterolContent": "1", "SodiumContent": "2", "CarbohydrateContent": "3.0",
        "FiberContent": "0.5", "SugarContent": "1.0", "ProteinContent": "0.5",
    }

    reader = build_csvreader_from_rows([row], tmp_path)
    recipe = reader.recipes[0]

    assert recipe.recipe_yield == "Not specified"

def test_images_parsing(tmp_path):
    row_with_images = {
        "RecipeId": "1", "Name": "Test A", "AuthorId": "1", "AuthorName": "Author A", "RecipeCategory": "Category",
        "CookTime": "10", "PrepTime": "5", "DatePublished": "5th Sep 2015", "Description": "desc",
        "Images": "['https://example.com/img1.jpg', 'https://example.com/img2.jpg']",
        "RecipeIngredientQuantities": "['1']", "RecipeIngredientParts": "['sugar']", "RecipeInstructions": "['Mix']",
        "RecipeServings": "2", "RecipeYield": "NA",
        "Calories": "100", "FatContent": "5.0", "SaturatedFatContent": "2.0",
        "CholesterolContent": "10", "SodiumContent": "20", "CarbohydrateContent": "30",
        "FiberContent": "2.0", "SugarContent": "15.0", "ProteinContent": "5.0",
    }
    reader = build_csvreader_from_rows([row_with_images], tmp_path)
    recipe = reader.recipes[0]
    assert isinstance(recipe.images, list)
    assert recipe.images == ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]


def test_date_parsed_correctly(tmp_path):
    row = {
        "RecipeId": "3", "Name": "Z", "AuthorId": "2", "AuthorName": "B", "RecipeCategory": "D",
        "CookTime": "1", "PrepTime": "2", "TotalTime": "3", "DatePublished": "9th Aug 2009", "Description": "",
        "Images": "",
        "RecipeIngredientQuantities": "['1']",
        "RecipeIngredientParts": "['salt']",
        "RecipeInstructions": "['Do']",
        "Calories": "1", "FatContent": "0.1", "SaturatedFatContent": "0.0",
        "CholesterolContent": "0", "SodiumContent": "0", "CarbohydrateContent": "0.0",
        "FiberContent": "0.0", "SugarContent": "0.0", "ProteinContent": "0.0",
        "RecipeServings": "1", "RecipeYield": "NA",
    }

    reader = build_csvreader_from_rows([row], tmp_path)
    recipe = reader.recipes[0]
    assert isinstance(recipe.date, datetime)
    assert recipe.date == datetime(2009, 8, 9)


# py -m pytest -v tests/unit/test_csv_reader.py
# Run from project root, to see the specific tests that were run
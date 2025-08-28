import os
import csv
import ast
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe

class CSVDataReader:
    def __init__(self, csv_path):
        self.__csv_path = csv_path
        self.__recipes = []
        self.__authors = {}
        self.__categories = {}

    def csv_read(self):
        with open(self.__csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                #CREATION OF AUTHOR
                author_id = int(row["AuthorId"])
                author = self.__authors.get(author_id)
                if author is None:
                    author = Author(author_id, row["AuthorName"])
                    self.__authors[author_id] = author

                #CREATION OF CATEGORY
                category_name = row["RecipeCategory"].strip()
                category = self.__categories.get(category_name)
                if category is None:
                    category = Category(category_name)
                    self.__categories[category_name] = category

                #CREATION OF NUTRITION
                nutrition = Nutrition(
                    nutrition_id=int(row["RecipeId"]),
                    calories=int(float(row["Calories"])) if row["Calories"] else 0,
                    fat=float(row["FatContent"]) if row["FatContent"] else 0.0,
                    saturated_fat=float(row["SaturatedFatContent"]) if row["SaturatedFatContent"] else 0.0,
                    cholesterol=int(float(row["CholesterolContent"])) if row["CholesterolContent"] else 0,
                    sodium=int(float(row["SodiumContent"])) if row["SodiumContent"] else 0,
                    carbohydrates=float(row["CarbohydrateContent"]) if row["CarbohydrateContent"] else 0.0,
                    fiber=float(row["FiberContent"]) if row["FiberContent"] else 0.0,
                    sugar=float(row["SugarContent"]) if row["SugarContent"] else 0.0,
                    protein=float(row["ProteinContent"]) if row["ProteinContent"] else 0.0,
                )

                # INGREDIENTS
                ingredient_quantities = ast.literal_eval(row["RecipeIngredientQuantities"]) if row[
                    "RecipeIngredientQuantities"] else []
                ingredients = ast.literal_eval(row["RecipeIngredientParts"]) if row[
                    "RecipeIngredientParts"] else []

                # INSTRUCTIONS
                instructions = ast.literal_eval(row["RecipeInstructions"]) if row["RecipeInstructions"] else []

                # YIELD VALUE
                yield_value = row["RecipeYield"].strip() if row["RecipeYield"] else ""
                recipe_yield = "Not specified" if not yield_value or yield_value == "NA" else yield_value

                # IMAGES
                images = ast.literal_eval(row.get("Images")) if row.get("Images") else []

                #RECIPE
                recipe = Recipe(
                    recipe_id=int(row["RecipeId"]),
                    name=row["Name"].strip(),
                    author=author,
                    cook_time=row["CookTime"],
                    preparation_time=row["PrepTime"],
                    description=row["Description"],
                    images=images,
                    category=category,
                    ingredient_quantities=ingredient_quantities,
                    ingredients=ingredients,
                    nutrition=nutrition,
                    servings=row["RecipeServings"],
                    recipe_yield=recipe_yield,
                    instructions=instructions
                )

                #UPDATE RELATIONSHIPS
                self.__recipes.append(recipe)
                author.add_recipe(recipe)
                category.add_recipe(recipe)

    # Accessors
    @property
    def recipes(self):
        return self.__recipes

    @property
    def authors(self):
        return list(self.__authors.values())

    @property
    def categories(self):
        return list(self.__categories.values())
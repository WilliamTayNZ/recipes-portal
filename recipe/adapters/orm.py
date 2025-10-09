from sqlalchemy import Table, Column, Integer, Float, String, DateTime, ForeignKey

from sqlalchemy.orm import registry, relationship

from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.user import User
# from recipe.domainmodel.recipe_image import RecipeImage
# from recipe.domainmodel.recipe_instruction import RecipeInstruction
# from recipe.domainmodel.recipe_ingredient import RecipeIngredient

mapper_registry = registry()

def map_model_to_tables():
    # TODO: implement mapping logic for your models and tables
    pass
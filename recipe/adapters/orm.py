from sqlalchemy import Table, Column, Integer, Float, String, DateTime, ForeignKey

from sqlalchemy.orm import registry, relationship

from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.user import User
from recipe.domainmodel.recipe_image import RecipeImage
from recipe.domainmodel.recipe_instruction import RecipeInstruction
from recipe.domainmodel.recipe_ingredient import RecipeIngredient

mapper_registry = registry()

# recipe table
recipe_table = Table('recipe', mapper_registry.metadata,
                      Column('id', Integer, primary_key=True, autoincrement=True),
                      Column('name', String(255), nullable=False),
                      Column('cook_time', Integer),
                      Column('preparation_time', Integer),
                      Column('date', DateTime),
                      Column('description', String(255)),
                      Column('images', List, nullable=False),
                      Column('ingredient_quantities', List, nullable=False),
                      Column('ingredients', List, nullable=False),
                      Column('rating', Float),
                      Column('servings', String(255)),
                      Column('recipe_yield', String(255)),
                      Column('instructions', List, nullable=False),
                      Column('category_id', Integer, ForeignKey('category.id')),
                      Column('nutrition_id', Integer, ForeignKey('nutrition.id'), unique=True),
                      Column('author_id', Integer, ForeignKey('author.id')),
                      )

# nutrition table
nutrition_table = Table('nutrition', mapper_registry.metadata,
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('calories', Float, nullable=False),
                        Column('fat', Float, nullable=False),
                        Column('saturated_fat', Float, nullable=False),
                        Column('cholesterol', Float, nullable=False),
                        Column('sodium', Float, nullable=False),
                        Column('carbohydrates', Float, nullable=False),
                        Column('fiber', Float, nullable=False),
                        Column('sugar', Float, nullable=False),
                        Column('protein', Float, nullable=False),
                        )

# recipe image table
recipe_image_table = Table('recipe_image', mapper_registry.metadata,
                           Column('id', Integer, primary_key=True, autoincrement=True),
                           Column('recipe_id', Integer, ForeignKey('recipe.id')),
                           Column('image_url', String(255), nullable=False),
                           Column('position', Integer, nullable=False)
                           )

# recipe instruction table
recipe_instruction_table = Table('recipe_instruction', mapper_registry.metadata,
                                 Column('id', Integer, primary_key=True, autoincrement=True),
                                 Column('recipe_id', Integer, ForeignKey('recipe.id')),
                                 Column('instruction', String(255))
                                 Column('position', Integer, nullable=False)
                                 )

# recipe ingredient table
recipe_ingredient_table = Table('recipe_ingredient', mapper_registry.metadata,
                                Column('id', Integer, primary_key=True, autoincrement=True),
                                Column('recipe_id', Integer, ForeignKey('recipe.id')),
                                Column('ingredient', String(255), nullable=False),
                                Column('ingredient_quantity', String(255))
                                Column('position', Integer, nullable=False)
                                )

# author table
author_table = Table('author', mapper_registry.metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('name', String(255), nullable=False),
                     )

# category table
category_table = Table('category', mapper_registry.metadata,
                       Column('id', Integer, primary_key=True, autoincrement=True),
                       Column('name', String(255), nullable=False, unique=True),
                       )

# user table
user_table = Table('user', mapper_registry.metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('username', String(255), unique=True, nullable=False),
                   Column('password', String(255), nullable=False),
                   )

# favourite table
favourite_table = Table('favourite', mapper_registry.metadata,
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('user_id', Integer, ForeignKey('user.id')),
                        Column('recipe_id', Integer, ForeignKey('recipe.id'), nullable=False),
                        )

# review table
review_table = Table('review', mapper_registry.metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('recipe_id', Integer, ForeignKey('recipe.id'), nullable=False),
                     Column('rating', Integer, nullable=False),
                     Column('review_comment', String(255), nullable=False),
                     Column('date', DateTime, nullable=False),
                     )


# ORM mappings
def map_model_to_tables():
    # recipe mapping
    mapper_registry.map_imperatively(Recipe, recipe_table, properties={
        '_Recipe__id': recipe_table.c.id,
        '_Recipe__name': recipe_table.c.name,
        '_Recipe__cook_time': recipe_table.c.cook_time,
        '_Recipe__preparation_time': recipe_table.c.preparation_time,
        '_Recipe__date': recipe_table.c.date,
        '_Recipe__description': recipe_table.c.description,
        '_Recipe__images': recipe_table.c.images,
        '_Recipe__ingredient_quantities': recipe_table.c.ingredient_quantities,
        '_Recipe__ingredients': recipe_table.c.ingredients,
        '_Recipe__rating': recipe_table.c.rating,
        '_Recipe__servings': recipe_table.c.servings,
        '_Recipe__recipe_yield': recipe_table.c.recipe_yield,
        '_Recipe__instructions': recipe_table.c.instructions,
        '_Recipe__category': relationship(Category, back_populates="_Category__recipes"),
        '_Recipe__nutrition': relationship(Nutrition, back_populates="_Nutrition__recipe"),
        '_Recipe__author': relationship(Author, back_populates="_Author__recipes"),
        # '_Recipe__images': relationship(RecipeImage, back_populates="_Images__recipe"),
        # '_Recipe__instructions': relationship(RecipeInstruction, back_populates="_RecipeInstruction__recipe"),
        # '_Recipe__ingredients': relationship(RecipeIngredient, back_populates="_Ingredient__recipe"),
    })

    # nutrition mapping
    mapper_registry.map_imperatively(Nutrition, nutrition_table, properties={
        '_Nutrition__nutrition_id': nutrition_table.c.id,
        '_Nutrition__calories': nutrition_table.c.calories,
        '_Nutrition__fat': nutrition_table.c.fat,
        '_Nutrition__saturated_fat': nutrition_table.c.saturated_fat,
        '_Nutrition__cholesterol': nutrition_table.c.cholesterol,
        '_Nutrition__sodium': nutrition_table.c.sodium,
        '_Nutrition__carbohydrates': nutrition_table.c.carbohydrates,
        '_Nutrition__fiber': nutrition_table.c.fiber,
        '_Nutrition__sugar': nutrition_table.c.sugar,
        '_Nutrition__protein': nutrition_table.c.protein,
        '_Nutrition__recipe': relationship(Recipe, back_populates="_Recipe__nutrition"),
    })

    # recipe image mapping
    mapper_registry.map_imperatively(RecipeImage, recipe_image_table, properties={
        '_RecipeImage__id': recipe_image_table.c.id,
        '_RecipeImage__recipe_id': recipe_image_table.c.recipe_id,
        '_RecipeImage__url': recipe_image_table.c.image_url,
        '_RecipeImage__position': recipe_image_table.c.position
        # '_RecipeImage__recipe': relationship(Recipe, back_populates="_Recipe__images"),
    })

    # recipe instruction mapping
    mapper_registry.map_imperatively(RecipeInstruction, recipe_instruction_table, properties={
        '_RecipeInstruction__id': recipe_instruction_table.c.id,
        '_RecipeInstruction__recipe_id': recipe_instruction_table.c.recipe_id,
        '_RecipeInstruction__step': recipe_instruction_table.c.instruction,
        '_RecipeInstruction__position': recipe_instruction_table.c.position
        # '_RecipeInstruction__recipe': relationship(Recipe, back_populates="_Recipe__instructions"),
    })

    # recipe ingredient mapping
    mapper_registry.map_imperatively(RecipeIngredient, recipe_ingredient_table, properties={
        '_RecipeIngredient__id': recipe_ingredient_table.c.id,
        '_RecipeIngredient__recipe_id': recipe_ingredient_table.c.recipe_id,
        '_RecipeIngredient__ingredient': recipe_ingredient_table.c.ingredient,
        '_RecipeIngredient__quantity': recipe_ingredient_table.c.ingredient_quantity,
        '_RecipeIngredient__position': recipe_ingredient_table.c.position
        # '_RecipeIngredient__recipe': relationship(Recipe, back_populates="_Recipe__ingredients"),
    })

    # author mapping
    mapper_registry.map_imperatively(Author, author_table, properties={
        '_Author__id': author_table.c.id,
        '_Author__name': author_table.c.name,
        '_Author__recipes': relationship(Recipe, back_populates="_Recipe__author")
    })

    # category mapping
    mapper_registry.map_imperatively(Category, category_table, properties={
        '_Category__id': category_table.c.id,
        '_Category__name': category_table.c.name,
        '_Category__recipes': relationship(Recipe, back_populates="_Recipe__category")
    })

    # user mapping
    mapper_registry.map_imperatively(User, user_table, properties={
        '_User__id': user_table.c.id,
        '_User__username': user_table.c.username,
        '_User__password': user_table.c.password,
        '_User__favourite_recipes': relationship(Favourite, back_populates="_Favourite__user"),
        '_User__reviews': relationship(Review, back_populates="_Review__user")
    })

    # favourite mapping
    mapper_registry.map_imperatively(Favourite, favourite_table, properties={
        '_Favourite__favourite_id': favourite_table.c.id,
        '_Favourite__user_id': favourite_table.c.user_id,
        '_Favourite__user': relationship(User, back_populates="_User__favourite_recipes"),
        '_Favourite__recipe_id': favourite_table.c.recipe_id
    })

    # review mapping
    mapper_registry.map_imperatively(Review, review_table, properties={
        '_Review__review_id': review_table.c.id,
        # '_Review__user_id': review_table.c.user_id,
        '_Review__user': relationship(User, back_populates="_User__reviews"),
        '_Review__recipe_id': review_table.c.recipe_id,
        '_Review__rating': review_table.c.rating,
        '_Review__review_comment': review_table.c.review_comment,
        '_Review__date': review_table.c.date
    })
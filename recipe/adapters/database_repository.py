from datetime import date
from typing import List
from sqlalchemy import desc, asc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import scoped_session


from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.user import User
from recipe.domainmodel.recipe_image import RecipeImage
from recipe.domainmodel.recipe_ingredient import RecipeIngredient
from recipe.domainmodel.recipe_instruction import RecipeInstruction

from recipe.adapters.repository import AbstractRepository


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if self.__session is not None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    # ====================
    # Session Management
    # ====================

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    # ====================
    # Recipe Methods
    # ====================

    def add_recipe(self, recipe: Recipe):
        with self._session_cm as scm:
            scm.session.add(recipe)
            scm.commit()
            
            # Create and save individual RecipeImage objects
            for position, image_url in enumerate(recipe.images, 1):
                recipe_image = RecipeImage(recipe.id, image_url, position)
                scm.session.add(recipe_image)
            
            # Create and save individual RecipeIngredient objects
            for position, (quantity, ingredient) in enumerate(zip(recipe.ingredient_quantities, recipe.ingredients), 1):
                recipe_ingredient = RecipeIngredient(recipe.id, quantity, ingredient, position)
                scm.session.add(recipe_ingredient)
            
            # Create and save individual RecipeInstruction objects
            for position, instruction in enumerate(recipe.instructions, 1):
                recipe_instruction = RecipeInstruction(recipe.id, instruction, position)
                scm.session.add(recipe_instruction)
            
            scm.commit()

    def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        try:
            recipe = self._session_cm.session.query(Recipe).filter(
                Recipe._Recipe__id == recipe_id
            ).one()
            self._populate_recipe_data(recipe)
            return recipe
        except NoResultFound:
            return None

    def get_number_of_recipe(self) -> int:
        with self._session_cm as scm:
            return scm.session.query(Recipe).count()

    def get_first_recipe(self) -> Recipe:
        with self._session_cm as scm:
            recipe = scm.session.query(Recipe).order_by(asc(Recipe._Recipe__id)).first()
            if recipe:
                self._populate_recipe_data(recipe)
            return recipe

    def get_last_recipe(self) -> Recipe:
        with self._session_cm as scm:
            recipe = scm.session.query(Recipe).order_by(desc(Recipe._Recipe__id)).first()
            if recipe:
                self._populate_recipe_data(recipe)
            return recipe

    def get_recipes(self) -> List[Recipe]:
        with self._session_cm as scm:
            recipes = scm.session.query(Recipe).all()
            self._bulk_populate_recipes(recipes, scm.session)
            return recipes

    def get_recipes_by_id(self, id_list: List[int]) -> List[Recipe]:
        if not id_list:
            return []
        with self._session_cm as scm:
            recipes = scm.session.query(Recipe).filter(Recipe._Recipe__id.in_(id_list)).all()
            self._bulk_populate_recipes(recipes, scm.session)
            return recipes

    def get_recipes_by_name(self, name: str) -> List[Recipe]:
        with self._session_cm as scm:
            query = scm.session.query(Recipe)
            if name:
                query = query.filter(Recipe._Recipe__name.ilike(f"%{name}%"))
            recipes = query.order_by(asc(Recipe._Recipe__name)).all()
            self._bulk_populate_recipes(recipes, scm.session)
            return recipes

    # ====================
    # Author Methods
    # ====================

    def add_author(self, author: Author):
        with self._session_cm as scm:
            scm.session.add(author)
            scm.commit()

    def get_authors_by_name(self, author_name: str):
        with self._session_cm as scm:
            authors = scm.session.query(Author).filter(
                Author._Author__name.ilike(f"%{author_name}%")
            ).all()
            return authors

    def get_recipes_by_author_name(self, author_name: str) -> List[Recipe]:
        with self._session_cm as scm:
            recipes = scm.session.query(Recipe).join(Author).filter(
                Author._Author__name.ilike(f"%{author_name}%")
            ).all()
            self._bulk_populate_recipes(recipes, scm.session)
            return recipes

    # ====================
    # Category Methods
    # ====================

    def add_category(self, category: Category):
        with self._session_cm as scm:
            scm.session.add(category)
            scm.commit()

    def get_category_by_name(self, category_name: str):
        with self._session_cm as scm:
            category = scm.session.query(Category).filter(
                Category._Category__name == category_name
            ).first()
            return category

    def get_recipes_by_category_name(self, category_name: str) -> List[Recipe]:
        with self._session_cm as scm:
            recipes = scm.session.query(Recipe).join(Category).filter(
                Category._Category__name == category_name
            ).all()
            self._bulk_populate_recipes(recipes, scm.session)
            return recipes

    # ====================
    # Review Methods
    # ====================

    def add_review(self, review: Review):
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def delete_review(self, review_id: int, username: str):
        with self._session_cm as scm:
            try:
                review = scm.session.query(Review).filter(
                    Review._Review__review_id == review_id
                ).one()
                if review.user.username == username:
                    scm.session.delete(review)
                    scm.commit()
                    return True
                return False
            except NoResultFound:
                return False

    # ====================
    # Favourite Methods
    # ====================

    def add_favourite(self, user: User, recipe: Recipe):
        if not user or not recipe:
            return
        with self._session_cm as scm:
            existing = scm.session.query(Favourite).filter(
                Favourite._Favourite__user_id == user.id,
                Favourite._Favourite__recipe_id == recipe.id
            ).first()
            if not existing:
                fav = Favourite(user=user, recipe=recipe)
                scm.session.add(fav)
                scm.commit()

    def remove_favourite(self, user: User, recipe: Recipe):
        if not user or not recipe:
            return
        with self._session_cm as scm:
            scm.session.query(Favourite).filter(
                Favourite._Favourite__user_id == user.id,
                Favourite._Favourite__recipe_id == recipe.id
            ).delete()
            scm.commit()

    def get_user_favourites(self, username: str) -> List[Recipe]:
        user = self.get_user(username)
        if not user:
            return []
        with self._session_cm as scm:
            favourites = scm.session.query(Favourite).filter(
                Favourite._Favourite__user_id == user.id
            ).all()
            return [fav.recipe for fav in favourites if fav.recipe is not None]

    def is_recipe_in_favourites(self, username: str, recipe_id: int) -> bool:
        user = self.get_user(username)
        if not user:
            return False
        with self._session_cm as scm:
            favourite = scm.session.query(Favourite).filter(
                Favourite._Favourite__user_id == user.id,
                Favourite._Favourite__recipe_id == recipe_id
            ).first()
            return favourite is not None

    # ====================
    # User Methods
    # ====================

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, username: str) -> User:
        try:
            query = self._session_cm.session.query(User).filter(
                User._User__username == username
            )
            user = query.one()
            return user
        except NoResultFound:
            return None

    # ====================
    # Utility Helpers
    # ====================

    def _populate_recipe_data(self, recipe: Recipe):
        """Populate a Recipe object with related data (images, ingredients, instructions)"""
        if recipe is None:
            return
        with self._session_cm as scm:
            self._populate_recipe_data_in_session(recipe, scm.session)

    def _populate_recipe_data_in_session(self, recipe: Recipe, session):
        if recipe is None:
            return

        # Query individual objects from their tables and populate Recipe lists
        recipe_images = session.query(RecipeImage).filter(
            RecipeImage._RecipeImage__recipe_id == recipe.id
        ).order_by(RecipeImage._RecipeImage__position).all()
        recipe._Recipe__images = [img.url for img in recipe_images]

        recipe_ingredients = session.query(RecipeIngredient).filter(
            RecipeIngredient._RecipeIngredient__recipe_id == recipe.id
        ).order_by(RecipeIngredient._RecipeIngredient__position).all()
        recipe._Recipe__ingredients = [ing.ingredient for ing in recipe_ingredients]
        recipe._Recipe__ingredient_quantities = [ing.quantity for ing in recipe_ingredients]

        recipe_instructions = session.query(RecipeInstruction).filter(
            RecipeInstruction._RecipeInstruction__recipe_id == recipe.id
        ).order_by(RecipeInstruction._RecipeInstruction__position).all()
        recipe._Recipe__instructions = [inst.step for inst in recipe_instructions]

    def _bulk_populate_recipes(self, recipes: List[Recipe], session):
        """Bulk populate multiple recipes with related data to avoid N+1 queries"""
        if not recipes:
            return
        
        recipe_ids = [recipe.id for recipe in recipes]
        
        # Use more efficient queries with explicit column selection
        # Bulk load all images for all recipes
        recipe_images = session.query(RecipeImage).filter(
            RecipeImage._RecipeImage__recipe_id.in_(recipe_ids)
        ).order_by(RecipeImage._RecipeImage__recipe_id, RecipeImage._RecipeImage__position).all()
        
        # Bulk load all ingredients for all recipes
        recipe_ingredients = session.query(RecipeIngredient).filter(
            RecipeIngredient._RecipeIngredient__recipe_id.in_(recipe_ids)
        ).order_by(RecipeIngredient._RecipeIngredient__recipe_id, RecipeIngredient._RecipeIngredient__position).all()
        
        # Bulk load all instructions for all recipes
        recipe_instructions = session.query(RecipeInstruction).filter(
            RecipeInstruction._RecipeInstruction__recipe_id.in_(recipe_ids)
        ).order_by(RecipeInstruction._RecipeInstruction__recipe_id, RecipeInstruction._RecipeInstruction__position).all()
        
        # Group by recipe_id for efficient lookup
        images_by_recipe = {}
        for img in recipe_images:
            if img.recipe_id not in images_by_recipe:
                images_by_recipe[img.recipe_id] = []
            images_by_recipe[img.recipe_id].append(img.url)
        
        ingredients_by_recipe = {}
        quantities_by_recipe = {}
        for ing in recipe_ingredients:
            if ing.recipe_id not in ingredients_by_recipe:
                ingredients_by_recipe[ing.recipe_id] = []
                quantities_by_recipe[ing.recipe_id] = []
            ingredients_by_recipe[ing.recipe_id].append(ing.ingredient)
            quantities_by_recipe[ing.recipe_id].append(ing.quantity)
        
        instructions_by_recipe = {}
        for inst in recipe_instructions:
            if inst.recipe_id not in instructions_by_recipe:
                instructions_by_recipe[inst.recipe_id] = []
            instructions_by_recipe[inst.recipe_id].append(inst.step)
        
        # Populate each recipe
        for recipe in recipes:
            recipe._Recipe__images = images_by_recipe.get(recipe.id, [])
            recipe._Recipe__ingredients = ingredients_by_recipe.get(recipe.id, [])
            recipe._Recipe__ingredient_quantities = quantities_by_recipe.get(recipe.id, [])
            recipe._Recipe__instructions = instructions_by_recipe.get(recipe.id, [])

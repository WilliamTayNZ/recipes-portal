class Favourite:
    def __init__(self, user_id=None, user=None, recipe=None, recipe_id=None):
        # Infer user_id from User if not explicitly provided
        try:
            from recipe.domainmodel.user import User
            if user_id is None and isinstance(user, User):
                user_id = user.id
        except Exception:
            pass
        self.__user_id = user_id

        # Handle user relationship or placeholder for tests
        try:
            from recipe.domainmodel.user import User
            if isinstance(user, User):
                self.__user = user  # ORM relationship-compatible
            else:
                self.__user_placeholder = user
        except Exception:
            self.__user_placeholder = user

        # Normalise recipe/recipe_id for both memory and DB
        rid = recipe_id
        try:
            from recipe.domainmodel.recipe import Recipe
            if rid is None and hasattr(recipe, 'id'):
                rid = getattr(recipe, 'id')
            if isinstance(recipe, Recipe):
                self.__recipe = recipe
            else:
                # keep placeholder for tests (e.g., a string)
                self.__recipe = recipe
        except Exception:
            self.__recipe = recipe
        self.__recipe_id = rid

    def __repr__(self):
        rid = self.__recipe_id if self.__recipe_id is not None else getattr(self.__recipe, 'id', self.__recipe)
        return f"Favourite(user_id={self.__user_id}, recipe_id={rid})"

    def __eq__(self, other):
        # Prefer recipe_id when available, otherwise compare recipe placeholder/object
        self_rid = self.__recipe_id if self.__recipe_id is not None else self.__recipe
        other_rid = getattr(other, '_Favourite__recipe_id', None)
        if other_rid is None:
            other_rid = getattr(other, '_Favourite__recipe', None)
        return self.__user_id == getattr(other, '_Favourite__user_id', None) and self_rid == other_rid

    def __lt__(self, other):
        self_val = self.__recipe_id if self.__recipe_id is not None else self.__recipe
        other_val = getattr(other, '_Favourite__recipe_id', None)
        if other_val is None:
            other_val = getattr(other, '_Favourite__recipe', None)
        return self_val < other_val

    def __hash__(self):
        key = self.__recipe_id if self.__recipe_id is not None else self.__recipe
        return hash((self.__user_id, key))

    @property
    def user_id(self):
        return self.__user_id

    @property
    def user(self):
        # Prefer ORM relationship if present; otherwise return placeholder used in unit tests
        if hasattr(self, '_Favourite__user'):
            return self.__user
        return getattr(self, '_Favourite__user_placeholder', None)

    @property
    def recipe(self):
        return self.__recipe

    @property
    def recipe_id(self):
        return self.__recipe_id
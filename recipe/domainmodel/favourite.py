class Favourite:
    def __init__(self, user_id, user, recipe):
        self.__user_id = user_id
        self.__user = user
        self.__recipe = recipe

    def __repr__(self):
        return f"Favourite(user_id={self.__user_id}, recipe_id={getattr(self.__recipe, 'id', self.__recipe)})"

    def __eq__(self, other):
        return self.__user_id == other.__user_id and self.__recipe == other.__recipe

    def __lt__(self, other):
        return self.__recipe < other.__recipe

    def __hash__(self):
        return hash((self.__user_id, self.__recipe))

    @property
    def user_id(self):
        return self.__user_id

    @property
    def user(self):
        return self.__user

    @property
    def recipe(self):
        return self.__recipe
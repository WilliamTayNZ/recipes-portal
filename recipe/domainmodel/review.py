from recipe import Recipe
from user import User


class Review:
# TODO: Complete the implementation of the Review class.
    def __init__(self, author_id: int, name: str, recipe: Recipe, rating : float, user_id : User, review : str):
        self.__author_id = author_id
        self.__name = name
        self.__recipe = recipe
        self.__rating = rating
        self.__user_id = user_id
        self.__review = review

    def __repr__(self) -> str:
        return f"<Rating {self.rating}>"

    def __eq__(self, other):
        if not isinstance(other, Review):
            return False
        return self.rating == other.rating

    def __lt__(self, other):
        if not isinstance(other, Review):
            raise TypeError("Comparison must be between Review instances")
        return self.rating < other.rating

    def __hash__(self):
        return hash(self.rating)

    @property
    def author_id(self):
        return self.__author_id

    @property
    def name(self):
        return self.__name

    @property
    def recipe(self):
        return self.__recipe

    @property
    def rating(self):
        return self.__rating

    @property
    def user_id(self):
        return self.__user_id

    @property
    def review(self):
        return self.__review

    def add_rating(self, rating: float):
        self.__rating = rating
        return self


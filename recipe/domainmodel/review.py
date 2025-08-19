from recipe import Recipe
from user import User
from datetime import datetime

class Review:
    def __init__(self, review_id : int, user : User, recipe: Recipe, rating : float, review : str, date: datetime):
        self.__review_id = review_id
        self.__user = user
        self.__recipe = recipe
        self.__rating = rating
        self.__review = review
        self.__date = date

    def __repr__(self) -> str:
        return f"<User : {self.user.username} rated {self.recipe} {self.rating}/5 on {self.date} : {self.review}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Review):
            return False
        return self.rating == other.rating

    def __lt__(self, other) -> bool:
        if not isinstance(other, Review):
            raise TypeError("Comparison must be between Review instances")
        return self.rating < other.rating

    def __hash__(self) :
        return hash(self.rating)

    @property
    def review_id(self) -> int:
        return self.__review_id

    @property
    def user(self) -> User:
        return self.__user

    @property
    def recipe(self) -> Recipe:
        return self.__recipe

    @property
    def rating(self) -> float:
        return self.__rating

    @property
    def review(self) -> str:
        return self.__review

    @property
    def date(self) -> datetime:
        return self.__date

    def add_rating(self, rating: float):
        if not (0.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0 inclusive")
        self.__rating = rating
        return self

    def add_review(self, review: str):
        self.__review = review
        return self

    def add_date(self, date: datetime):
        self.__date = date
        return self
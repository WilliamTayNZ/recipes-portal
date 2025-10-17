from datetime import datetime

class Review:
    def __init__(self, user, recipe, rating, review_text, date=None, review_id: int = None):
        self.__id = review_id  # None for new reviews, will be set by database
        self.__user = user
        self.__recipe = recipe
        self.__rating = rating
        self.__review_text = review_text
        self.__date = date if date else datetime.now()

    def __repr__(self) -> str:
        return f"<User : {self.__user} rated {self.__recipe} {self.__rating}/5 on {self.__date} : {self.__review_text}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Review):
            return False
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Review):
            raise TypeError("Comparison must be between Review instances")
        return self.rating < other.rating

    def __hash__(self) :
        return hash(self.id)

    @property
    def id(self) -> int:
        return self.__id
    
    @id.setter
    def id(self, value: int):
        self.__id = value

    @property
    def user(self):
        return self.__user

    @property
    def rating(self):
        return self.__rating

    @property
    def recipe(self):
        return self.__recipe

    @property
    def review_text(self) -> str:
        return self.__review_text

    @property
    def date(self) -> datetime:
        return self.__date

    def add_rating(self, rating: float):
        if not (0.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0 inclusive")
        self.__rating = rating
        return self

    def add_review_text(self, review_text: str):
        self.__review_text = review_text
        return self

    def add_date(self, date: datetime):
        self.__date = date
        return self
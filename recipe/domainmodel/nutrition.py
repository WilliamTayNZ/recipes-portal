'''
Represents the nutritional information for a recipe.
Includes an ID and values such as calories, fat, cholesterol etc
Each instance stores the nutrition facts for a single recipe *per serving*,
allowing users to view and compare the health-related details of different recipes.
'''

class Nutrition:
    def __init__(self, nutrition_id: int, calories: int = 0, fat: float = 0.0, saturated_fat: float = 0.0,
                 cholesterol: int = 0, sodium: int = 0, carbohydrates: float = 0.0, fiber: float = 0.0,
                 sugar: float = 0.0, protein: float = 0.0):
        self.__id = nutrition_id
        self.__calories = calories  # kcal
        self.__fat = fat  # g
        self.__saturated_fat = saturated_fat  # g
        self.__cholesterol = cholesterol  # mg
        self.__sodium = sodium  # mg
        self.__carbohydrates = carbohydrates  # g
        self.__fiber = fiber  # g
        self.__sugar = sugar  # g
        self.__protein = protein  # g

    def health_star_rating(self):
        # Make sure required values exist
        if self.calories is None or self.sugar is None or self.saturated_fat is None \
           or self.sodium is None or self.fiber is None or self.protein is None:
            return None

        # Start at 5 stars
        score = 5.0

        # Deduct points for 'bad' nutrients
        score -= (self.saturated_fat / 5) * 0.5       # saturated fat penalty
        score -= (self.sugar / 10) * 0.3              # sugar penalty
        score -= (self.sodium / 1000) * 0.5           # sodium penalty

        # Add points for 'good' nutrients
        score += (self.fiber / 5) * 0.4               # fiber bonus
        score += (self.protein / 10) * 0.3            # protein bonus

        # Clamp between 0 and 5 stars
        return max(0.0, min(5.0, round(score, 1)))

    def __repr__(self) -> str:
        return (f"Nutrition(id={self.__id}, calories={self.__calories}, fat={self.__fat}, "
                f"saturated_fat={self.__saturated_fat}, cholesterol={self.__cholesterol}, "
                f"sodium={self.__sodium}, carbohydrates={self.__carbohydrates}, fiber={self.__fiber}, "
                f"sugar={self.__sugar}, protein={self.__protein})")

    def __eq__(self, other) -> bool:
        return isinstance(other, Nutrition) and self.id == other.id

    # For now, sorting is done by calories, but we might want the user to be able to sort by more attributes
    # Will ask a TA or lecturer
    def __lt__(self, other):
        return self.calories < other.calories

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self) -> int: # No setter for id
        return self.__id

    @property
    def calories(self) -> int:
        return self.__calories

    @calories.setter
    def calories(self, value: int) -> None:
        self.__calories = value

    @property
    def fat(self) -> float:
        return self.__fat

    @fat.setter
    def fat(self, value: float) -> None:
        self.__fat = value

    @property
    def saturated_fat(self) -> float:
        return self.__saturated_fat

    @saturated_fat.setter
    def saturated_fat(self, value: float) -> None:
        self.__saturated_fat = value

    @property
    def cholesterol(self) -> int:
        return self.__cholesterol

    @cholesterol.setter
    def cholesterol(self, value: int) -> None:
        self.__cholesterol = value

    @property
    def sodium(self) -> int:
        return self.__sodium

    @sodium.setter
    def sodium(self, value: int) -> None:
        self.__sodium = value

    @property
    def carbohydrates(self) -> float:
        return self.__carbohydrates

    @carbohydrates.setter
    def carbohydrates(self, value: float) -> None:
        self.__carbohydrates = value

    @property
    def fiber(self) -> float:
        return self.__fiber

    @fiber.setter
    def fiber(self, value: float) -> None:
        self.__fiber = value

    @property
    def sugar(self) -> float:
        return self.__sugar

    @sugar.setter
    def sugar(self, value: float) -> None:
        self.__sugar = value

    @property
    def protein(self) -> float:
        return self.__protein

    @protein.setter
    def protein(self, value: float) -> None:
        self.__protein = value


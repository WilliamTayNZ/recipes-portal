'''
Represents the nutritional information for a recipe.
Includes an ID and values such as calories, fat, cholesterol etc
Each instance stores the nutrition facts for a single recipe *per serving*,
allowing users to view and compare the health-related details of different recipes.
'''

class Nutrition:
    def __init__(self, nutrition_id: int, calories: int, fat: float, saturated_fat: float,
                 cholesterol: int, sodium: int, carbohydrates: float, fiber: float,
                 sugar: float, protein: float):
        self.__id = nutrition_id
        self.__calories = calories
        self.__fat = fat
        self.__saturated_fat = saturated_fat
        self.__cholesterol = cholesterol
        self.__sodium = sodium
        self.__carbohydrates = carbohydrates
        self.__fiber = fiber
        self.__sugar = sugar
        self.__protein = protein

    def __repr__(self) -> str:
        return (f"Nutrition(id={self.__id}, calories={self.__calories}, fat={self.__fat}, "
                f"saturated_fat={self.__saturated_fat}, cholesterol={self.__cholesterol}, "
                f"sodium={self.__sodium}, carbohydrates={self.__carbohydrates}, fiber={self.__fiber}, "
                f"sugar={self.__sugar}, protein={self.__protein})")

    def __eq__(self, other) -> bool:
        return self.id == other.id

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


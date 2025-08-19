import os
import csv
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe

class CSVDataReader:
    def __init__(self, csv_path):
        self.__csv_path = csv_path
        self.__recipes = []

    def csv_read(self):
        with open(self.__csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

if __name__ == '__main__':
    csv_path = "./../data/recipes.csv"
    reader = CSVDataReader(csv_path)
    reader.csv_read()
import pytest

from flask import session

def test_browse_sort(client):
    # sort by alphabet
    response = client.get('/browse?category=None&sort=alphabet')
    page = response.get_data(as_text=True)

    first_recipe = 'Best Lemonade'
    second_recipe = 'Buttermilk Pie With Gingersnap Crumb Crust'

    assert first_recipe in page
    assert second_recipe in page
    assert page.index(first_recipe) < page.index(second_recipe)


def test_browse_category_filter(client):
    # filter by category using category name
    response = client.get('/browse?category=Frozen Desserts&sort=')
    page = response.get_data(as_text=True)

    recipe_in_category = 'Low-Fat Berry Blue Frozen Dessert'
    recipe_not_in_category = 'Best Lemonade'

    assert recipe_in_category in page
    assert recipe_not_in_category not in page


def test_browse_sort_and_filter(client):
    # sort by alphabet and filter by category using category name
    response = client.get('/browse?sort=alphabet&category=Chicken')
    page = response.get_data(as_text=True)

    recipe_in_category_1 = 'Warm Chicken A La King'
    recipe_in_category_2 = 'Chicken Breasts Lombardi'
    recipe_not_in_category = 'Low-Fat Berry Blue Frozen Dessert'

    assert recipe_in_category_1 in page
    assert recipe_in_category_2 in page
    assert recipe_not_in_category not in page

    # check sort order
    assert page.index(recipe_in_category_2) < page.index(recipe_in_category_1)
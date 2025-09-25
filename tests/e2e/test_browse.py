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

def test_search_by_name_returns_match(client):
    # search for a known recipe fragment
    resp = client.get('/browse?filter_by=name&query=lemonade')
    html = resp.get_data(as_text=True).lower()
    assert resp.status_code == 200
    assert 'lemonade' in html

def test_favourite_button_visible_when_logged_in(client):
    # Simulate logged-in session so templates render favourite forms
    with client.session_transaction() as sess:
        sess['user_name'] = 'test_user'

    resp = client.get('/browse')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # the card favourite form has class "card-fav-form"
    assert 'card-fav-form' in html

def test_search_case_insensitive(client):
    resp = client.get('/browse?filter_by=name&query=LEMONADE')
    html = resp.get_data(as_text=True).lower()
    assert resp.status_code == 200
    assert 'lemonade' in html

def test_empty_query_returns_browse_list(client):
    # when filter_by is provided but query is empty, browse should show (many) recipes
    resp = client.get('/browse?filter_by=name&query=')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # Ensure at least one card renders (template uses class="browse-card")
    assert 'class="browse-card"' in html

def test_no_results_shows_no_cards_and_no_pagination(client):
    resp = client.get('/browse?filter_by=name&query=thisshouldnotmatchanyrecipe')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # No recipe cards present
    assert 'class="browse-card"' not in html
    # No pagination links
    assert '/browse?cursor=' not in html

def test_no_heart_buttons_show_when_not_logged_in(client):
    resp = client.get('/browse')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    # the per-card favourite form and button should not be rendered for anonymous users
    assert 'card-fav-form' not in html
    assert 'card-fav-btn' not in html
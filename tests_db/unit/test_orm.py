import pytest
import datetime

from sqlalchemy.exc import IntegrityError

from recipe.domainmodel.user import User
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.review import Review
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.nutrition import Nutrition

recipe_date = datetime.datetime(2020, 2, 28)

def insert_user(empty_session, values=None):
    new_username = "Andrew"
    new_password = "1234"

    if values is not None:
        new_username = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO user (username, password) VALUES (:username, :password)',
                          {'username': new_username, 'password': new_password})
    row = empty_session.execute('SELECT id from user where username = :username',
                                {'username': new_username}).fetchone()
    return row[0]

def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO user (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from user'))
    keys = tuple(row[0] for row in rows)
    return keys

def insert_author(empty_session):
    empty_session.execute(
        'INSERT INTO author (name) VALUES ("Test Author")'
    )
    row = empty_session.execute('SELECT id from author').fetchone()
    return row[0]

def insert_category(empty_session):
    empty_session.execute(
        'INSERT INTO category (name) VALUES ("Test Category")'
    )
    row = empty_session.execute('SELECT id from category').fetchone()
    return row[0]

def insert_nutrition(empty_session):
    empty_session.execute(
        'INSERT INTO nutrition (calories, fat, saturated_fat, cholesterol, sodium, carbohydrates, fiber, sugar, protein) VALUES '
        '(100, 5.0, 2.0, 10, 200, 20.0, 3.0, 5.0, 8.0)'
    )
    row = empty_session.execute('SELECT id from nutrition').fetchone()
    return row[0]

def insert_recipe(empty_session):
    author_key = insert_author(empty_session)
    category_key = insert_category(empty_session)
    nutrition_key = insert_nutrition(empty_session)
    
    empty_session.execute(
        'INSERT INTO recipe (name, cook_time, preparation_time, date, description, rating, servings, recipe_yield, category_id, nutrition_id, author_id) VALUES '
        '("Test Recipe", 30, 15, :date, "A test recipe", 4.5, "4", "1 cake", :category_id, :nutrition_id, :author_id)',
        {'date': recipe_date.isoformat(), 'category_id': category_key, 'nutrition_id': nutrition_key, 'author_id': author_key}
    )
    row = empty_session.execute('SELECT id from recipe').fetchone()
    return row[0]

def insert_recipe_image(empty_session, recipe_id):
    empty_session.execute(
        'INSERT INTO recipe_image (recipe_id, image_url, position) VALUES '
        '(:recipe_id, "test_image.jpg", 1)',
        {'recipe_id': recipe_id}
    )
    row = empty_session.execute('SELECT id from recipe_image').fetchone()
    return row[0]

def insert_recipe_ingredient(empty_session, recipe_id):
    empty_session.execute(
        'INSERT INTO recipe_ingredient (recipe_id, ingredient, ingredient_quantity, position) VALUES '
        '(:recipe_id, "flour", "1 cup", 1)',
        {'recipe_id': recipe_id}
    )
    row = empty_session.execute('SELECT id from recipe_ingredient').fetchone()
    return row[0]

def insert_recipe_instruction(empty_session, recipe_id):
    empty_session.execute(
        'INSERT INTO recipe_instruction (recipe_id, instruction, position) VALUES '
        '(:recipe_id, "Mix ingredients", 1)',
        {'recipe_id': recipe_id}
    )
    row = empty_session.execute('SELECT id from recipe_instruction').fetchone()
    return row[0]

def insert_favourite(empty_session, user_id, recipe_id):
    empty_session.execute(
        'INSERT INTO favourite (user_id, recipe_id) VALUES '
        '(:user_id, :recipe_id)',
        {'user_id': user_id, 'recipe_id': recipe_id}
    )
    row = empty_session.execute('SELECT id from favourite').fetchone()
    return row[0]

def insert_review(empty_session, user_id, recipe_id):
    empty_session.execute(
        'INSERT INTO review (user_id, recipe_id, rating, review_comment, date) VALUES '
        '(:user_id, :recipe_id, 5, "Great recipe!", :date)',
        {'user_id': user_id, 'recipe_id': recipe_id, 'date': recipe_date.isoformat()}
    )
    row = empty_session.execute('SELECT id from review').fetchone()
    return row[0]

def make_user():
    user = User("Andrew", "111")
    return user

def make_author():
    author = Author(1, "Test Author")
    return author

def make_category():
    category = Category("Test Category")
    return category

def make_nutrition():
    nutrition = Nutrition(1, 100, 5.0, 2.0, 10, 200, 20.0, 3.0, 5.0, 8.0)
    return nutrition

def make_recipe():
    author = make_author()
    category = make_category()
    nutrition = make_nutrition()
    
    recipe = Recipe(
        1,
        "Test Recipe",
        author,
        cook_time=30,
        preparation_time=15,
        created_date=recipe_date,
        description="A test recipe",
        images=["test_image.jpg"],
        category=category,
        ingredient_quantities=["1 cup"],
        ingredients=["flour"],
        rating=4.5,
        nutrition=nutrition,
        servings="4",
        recipe_yield="1 cake",
        instructions=["Mix ingredients"]
    )
    return recipe

def test_loading_of_users(empty_session):
    users = list()
    users.append(("Andrew", "1234"))
    users.append(("Cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("Andrew", "1234"),
        User("Cindy", "1111")
    ]
    assert empty_session.query(User).all() == expected

def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM user'))
    assert rows == [("Andrew", "111")]

def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Andrew", "111")
        empty_session.add(user)
        empty_session.commit()

def test_loading_of_recipe(empty_session):
    recipe_key = insert_recipe(empty_session)
    expected_recipe = make_recipe()
    fetched_recipe = empty_session.query(Recipe).one()

    assert expected_recipe == fetched_recipe
    assert recipe_key == fetched_recipe.id

def test_loading_of_recipe_with_author(empty_session):
    recipe_key = insert_recipe(empty_session)
    
    recipe = empty_session.query(Recipe).get(recipe_key)
    author = empty_session.query(Author).filter(Author._Author__name == "Test Author").one()

    assert recipe.author == author
    assert author in recipe.author.recipes

def test_loading_of_recipe_with_category(empty_session):
    recipe_key = insert_recipe(empty_session)
    
    recipe = empty_session.query(Recipe).get(recipe_key)
    category = empty_session.query(Category).filter(Category._Category__name == "Test Category").one()

    assert recipe.category == category
    assert recipe in category.recipes

def test_loading_of_recipe_with_nutrition(empty_session):
    recipe_key = insert_recipe(empty_session)
    
    recipe = empty_session.query(Recipe).get(recipe_key)
    nutrition = empty_session.query(Nutrition).filter(Nutrition._Nutrition__calories == 100).one()

    assert recipe.nutrition == nutrition
    assert recipe == nutrition.recipe

def test_loading_of_recipe_with_images(empty_session):
    recipe_key = insert_recipe(empty_session)
    insert_recipe_image(empty_session, recipe_key)
    
    recipe = empty_session.query(Recipe).get(recipe_key)
    
    # The recipe should have the image populated
    assert len(recipe.images) == 1
    assert "test_image.jpg" in recipe.images

def test_loading_of_recipe_with_ingredients(empty_session):
    recipe_key = insert_recipe(empty_session)
    insert_recipe_ingredient(empty_session, recipe_key)
    
    recipe = empty_session.query(Recipe).get(recipe_key)
    
    # The recipe should have the ingredient populated
    assert len(recipe.ingredients) == 1
    assert "flour" in recipe.ingredients
    assert len(recipe.ingredient_quantities) == 1
    assert "1 cup" in recipe.ingredient_quantities

def test_loading_of_recipe_with_instructions(empty_session):
    recipe_key = insert_recipe(empty_session)
    insert_recipe_instruction(empty_session, recipe_key)
    
    recipe = empty_session.query(Recipe).get(recipe_key)
    
    # The recipe should have the instruction populated
    assert len(recipe.instructions) == 1
    assert "Mix ingredients" in recipe.instructions

def test_loading_of_favourite(empty_session):
    user_key = insert_user(empty_session, ("Andrew", "1234"))
    recipe_key = insert_recipe(empty_session)
    insert_favourite(empty_session, user_key, recipe_key)
    
    user = empty_session.query(User).filter(User._User__username == "Andrew").one()
    recipe = empty_session.query(Recipe).get(recipe_key)
    
    # Check that the favourite relationship exists
    favourites = empty_session.query(Favourite).filter(Favourite._Favourite__user_id == user_key).all()
    assert len(favourites) == 1
    assert favourites[0].recipe == recipe
    assert favourites[0].user == user

def test_loading_of_review(empty_session):
    user_key = insert_user(empty_session, ("Andrew", "1234"))
    recipe_key = insert_recipe(empty_session)
    insert_review(empty_session, user_key, recipe_key)
    
    user = empty_session.query(User).filter(User._User__username == "Andrew").one()
    recipe = empty_session.query(Recipe).get(recipe_key)
    
    # Check that the review relationship exists
    reviews = empty_session.query(Review).filter(Review._Review__user_id == user_key).all()
    assert len(reviews) == 1
    assert reviews[0].recipe == recipe
    assert reviews[0].user == user
    assert reviews[0].rating == 5
    assert reviews[0].review_comment == "Great recipe!"

def test_saving_of_recipe(empty_session):
    recipe = make_recipe()
    empty_session.add(recipe)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT name, cook_time, preparation_time, description, rating, servings, recipe_yield FROM recipe'))
    assert rows == [("Test Recipe", 30, 15, "A test recipe", 4.5, "4", "1 cake")]

def test_saving_of_author(empty_session):
    author = make_author()
    empty_session.add(author)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT name FROM author'))
    assert rows == [("Test Author",)]

def test_saving_of_category(empty_session):
    category = make_category()
    empty_session.add(category)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT name FROM category'))
    assert rows == [("Test Category",)]

def test_saving_of_nutrition(empty_session):
    nutrition = make_nutrition()
    empty_session.add(nutrition)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT calories, fat, protein FROM nutrition'))
    assert rows == [(100, 5.0, 8.0)]

def test_saving_of_favourite(empty_session):
    user = make_user()
    recipe = make_recipe()
    empty_session.add(user)
    empty_session.add(recipe)
    empty_session.commit()

    favourite = Favourite(user.id, user, recipe)
    empty_session.add(favourite)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, recipe_id FROM favourite'))
    assert rows == [(user.id, recipe.id)]

def test_saving_of_review(empty_session):
    user = make_user()
    recipe = make_recipe()
    empty_session.add(user)
    empty_session.add(recipe)
    empty_session.commit()

    review = Review(1, user, recipe, 5, "Great recipe!", recipe_date)
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, recipe_id, rating, review_comment FROM review'))
    assert rows == [(user.id, recipe.id, 5, "Great recipe!")]

def test_recipe_author_relationship(empty_session):
    author = make_author()
    recipe = make_recipe()
    
    # Establish bidirectional relationship
    author.add_recipe(recipe)
    
    empty_session.add(author)
    empty_session.commit()

    # Test that the relationship is properly established
    fetched_author = empty_session.query(Author).filter(Author._Author__name == "Test Author").one()
    fetched_recipe = empty_session.query(Recipe).filter(Recipe._Recipe__name == "Test Recipe").one()
    
    assert fetched_recipe in fetched_author.recipes
    assert fetched_recipe.author == fetched_author

def test_recipe_category_relationship(empty_session):
    category = make_category()
    recipe = make_recipe()
    
    # Establish bidirectional relationship
    category.add_recipe(recipe)
    
    empty_session.add(category)
    empty_session.commit()

    # Test that the relationship is properly established
    fetched_category = empty_session.query(Category).filter(Category._Category__name == "Test Category").one()
    fetched_recipe = empty_session.query(Recipe).filter(Recipe._Recipe__name == "Test Recipe").one()
    
    assert fetched_recipe in fetched_category.recipes
    assert fetched_recipe.category == fetched_category

def test_user_favourite_relationship(empty_session):
    user = make_user()
    recipe = make_recipe()
    empty_session.add(user)
    empty_session.add(recipe)
    empty_session.commit()

    favourite = Favourite(user.id, user, recipe)
    user.add_favourite_recipe(favourite)
    
    empty_session.add(favourite)
    empty_session.commit()

    # Test that the relationship is properly established
    fetched_user = empty_session.query(User).filter(User._User__username == "Andrew").one()
    fetched_favourite = empty_session.query(Favourite).filter(Favourite._Favourite__user_id == user.id).one()
    
    assert fetched_favourite in fetched_user.favourite_recipes
    assert fetched_favourite.user == fetched_user

def test_user_review_relationship(empty_session):
    user = make_user()
    recipe = make_recipe()
    empty_session.add(user)
    empty_session.add(recipe)
    empty_session.commit()

    review = Review(1, user, recipe, 5, "Great recipe!", recipe_date)
    user.add_review(review)
    
    empty_session.add(review)
    empty_session.commit()

    # Test that the relationship is properly established
    fetched_user = empty_session.query(User).filter(User._User__username == "Andrew").one()
    fetched_review = empty_session.query(Review).filter(Review._Review__user_id == user.id).one()
    
    assert fetched_review in fetched_user.reviews
    assert fetched_review.user == fetched_user
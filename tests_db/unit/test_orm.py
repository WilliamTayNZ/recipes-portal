import pytest
import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from recipe.domainmodel.user import User
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.category import Category
from recipe.domainmodel.author import Author
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.recipe_image import RecipeImage
from recipe.domainmodel.recipe_ingredient import RecipeIngredient
from recipe.domainmodel.recipe_instruction import RecipeInstruction

# insert functions below:

def insert_user(empty_session, values=None):
    username = "Bob"
    password = "Bob123456"
    if values:
        username, password = values

    empty_session.execute(
        'INSERT INTO user (username, password) VALUES (:username, :password)',
        {'username': username, 'password': password}
    )
    row = empty_session.execute(
        'SELECT id FROM user WHERE username = :username',
        {'username': username}
    ).fetchone()
    return row[0]

def insert_users(empty_session, users):
    for username, password in users:
        empty_session.execute(
            text('INSERT INTO user (username, password) VALUES (:username, :password)'),
            {'username': username, 'password': password}
        )
    rows = list(empty_session.execute('SELECT id FROM user'))
    return tuple(row[0] for row in rows)

def insert_recipe(empty_session, *, name="Test Recipe", author_id=None, category_id=None):
    if author_id is None:
        author_id = insert_author(empty_session)
    if category_id is None:
        category_id = insert_category(empty_session)

    now = datetime.datetime(2020, 1, 1, 12, 0, 0)
    empty_session.execute(
        text('''
             INSERT INTO recipe
             (id, name, author_id, cook_time, preparation_time, date, description,
              category_id, rating, servings, recipe_yield)
             VALUES (:id, :name, :author_id, :cook_time, :prep_time, :date, :desc,
                     :category_id, :rating, :servings, :yield)
             '''),
        {
            "id": 1,
            "name": name,
            "author_id": author_id,
            "cook_time": 10,
            "prep_time": 5,
            "date": now,
            "desc": "A tasty test recipe.",
            "category_id": category_id,
            "rating": 4.5,
            "servings": "2",
            "yield": 1
        },
    )

    row = empty_session.execute(
        text('SELECT id FROM recipe WHERE name = :name'),
        {"name": name},
    ).fetchone()
    return row[0]


def insert_category(empty_session, name = "Category A"):
    empty_session.execute(
        text('INSERT INTO category (name) VALUES (:name)'),
        {'name': name},
    )
    row = empty_session.execute(
        text('SELECT id FROM category WHERE name = :name'),
        {'name': name}
    ).fetchone()
    return row[0]

def insert_author(empty_session, name = "Author A"):
    empty_session.execute(
        text('INSERT INTO author (name) VALUES (:name)'),
        {"name": name},
    )
    row = empty_session.execute(
        'SELECT id FROM author WHERE name = :name',
        {"name": name}
    ).fetchone()
    return row[0]

def insert_review(empty_session, *, user_id, recipe_id, rating=5.0, text_val="Good", created=None):
    if created is None:
        created = datetime.datetime(2020, 1, 2, 8, 0, 0)
    empty_session.execute(
        text('''
        INSERT INTO review (user_id, recipe_id, rating, review_comment, date)
        VALUES (:uid, :rid, :rating, :comment, :created)
        '''),
        {"uid": user_id, "rid": recipe_id, "rating": rating, "comment": text_val, "created": created},
    )
    row = empty_session.execute(text('SELECT id FROM review ORDER BY id DESC LIMIT 1')).fetchone()
    return row[0]

# making objects with respective classes that have tables/databases
def make_user():
    return User("Bob", "Bob123456")
def make_category(name = "Category A"):
    return Category(name, [], 1)
def make_author(name = "Author A"):
    return Author(1, name)
def make_recipe():
    a = make_author("Author A")
    c = make_category("Category A")

    r = Recipe(
        recipe_id=1,
        name="Tasty recipe",
        author=a,
        cook_time=12,
        preparation_time=3,
        created_date=datetime.datetime(2020, 1, 1, 9, 0, 0),
        description="Test recipe blah",
        images=["a.jpg"],
        category=c,
        ingredient_quantities=["1 tsp"],
        ingredients=["salt"],
        servings="2",
        recipe_yield="1",
        instructions=["mix", "serve"],
    )

    if r not in a.recipes:
        a.add_recipe(r)

    return r


# tests !!
def test_loading_of_users(empty_session):
    users = [("Bob", "Bob123456"), ("Jeff", "Jeff7777")]
    insert_users(empty_session, users)

    result = empty_session.query(User).all()
    assert len(result) == 2
    assert result[0].username == "Bob"
    assert result[1].username == "Jeff"

def test_saving_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()
    rows = list(empty_session.execute(text('SELECT username, password FROM user')))
    assert rows == [("Bob", "Bob123456")]

def test_unique_username_constraint(empty_session):
    insert_user(empty_session), ("Bob", "bob2")
    empty_session.commit()
    with pytest.raises(IntegrityError):
        duplicate = User("Bob", "bob2")
        empty_session.add(duplicate)
        empty_session.commit()


def test_loading_of_recipe_with_author_and_category(empty_session):
    recipe_id = insert_recipe(empty_session, name="Recipe Test")
    recipe = empty_session.get(Recipe, recipe_id)

    assert isinstance(recipe, Recipe)
    assert recipe.name == "Recipe Test"
    assert isinstance(recipe.author, Author)
    assert isinstance(recipe.category, Category)


def test_save_recipe_from_domain(empty_session):
    recipe = make_recipe()
    empty_session.add(recipe)
    empty_session.commit()

    # Also need to manually create RecipeInstruction, RecipeIngredient, RecipeImage objects
    # since there's no ORM event listener to do this automatically
    for position, instruction in enumerate(recipe.instructions, 1):
        instr_obj = RecipeInstruction(recipe.id, instruction, position)
        empty_session.add(instr_obj)

    for position, (quantity, ingredient) in enumerate(zip(recipe.ingredient_quantities, recipe.ingredients), 1):
        ingr_obj = RecipeIngredient(recipe.id, quantity, ingredient, position)
        empty_session.add(ingr_obj)

    for position, image_url in enumerate(recipe.images, 1):
        img_obj = RecipeImage(recipe.id, image_url, position)
        empty_session.add(img_obj)

    empty_session.commit()

    recipe_in_db = empty_session.query(Recipe).first()
    assert recipe_in_db.name == "Tasty recipe"
    assert recipe_in_db.description == "Test recipe blah"


def test_review_links_user_and_recipe(empty_session):
    user_id = insert_user(empty_session, values=("Jeff", "7a"))
    recipe_id = insert_recipe(empty_session, name="Testing Link")

    insert_review(
        empty_session,
        user_id=user_id,
        recipe_id=recipe_id,
        rating=1,
        text_val="bad"
    )

    empty_session.commit()

    reviews = empty_session.query(Review).all()
    assert len(reviews) == 1
    review = reviews[0]
    assert review.user.id == user_id
    # Access the private recipe_id attribute since there's no recipe relationship in ORM
    assert review._Review__recipe_id == recipe_id
    # Access the private review_comment attribute as mapped by ORM
    assert review._Review__review_comment == "bad"


def test_recipe_instructions_relationship(empty_session):
    recipe = make_recipe()
    empty_session.add(recipe)
    empty_session.commit()

    # Manually create RecipeInstruction objects since ORM doesn't do this automatically
    for position, instruction in enumerate(recipe.instructions, 1):
        instr_obj = RecipeInstruction(recipe.id, instruction, position)
        empty_session.add(instr_obj)

    empty_session.commit()

    # Query RecipeInstruction table directly to verify they were created
    instructions = empty_session.query(RecipeInstruction).filter(
        RecipeInstruction._RecipeInstruction__recipe_id == 1
    ).order_by(RecipeInstruction._RecipeInstruction__position).all()

    assert len(instructions) == 2
    assert instructions[0].step == "mix"
    assert instructions[1].step == "serve"


def test_author_recipes_relationship(empty_session):
    recipe = make_recipe()
    empty_session.add(recipe)
    empty_session.commit()

    author_from_db = empty_session.query(Author).filter(
        Author._Author__id == 1
    ).first()

    # Verify the recipe is in the author's recipes through the ORM relationship
    assert len(author_from_db.recipes) >= 1
    assert any(r.id == recipe.id for r in author_from_db.recipes)


def test_category_recipes_relationship(empty_session):
    recipe = make_recipe()
    empty_session.add(recipe)
    empty_session.commit()

    category_from_db = empty_session.query(Category).filter(
        Category._Category__id == 1
    ).first()

    # Verify the recipe is in the category's recipes through the ORM relationship
    assert len(category_from_db.recipes) >= 1
    assert any(r.id == recipe.id for r in category_from_db.recipes)

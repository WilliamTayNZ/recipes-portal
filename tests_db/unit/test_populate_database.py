from sqlalchemy import select, inspect

from recipe.adapters.orm import mapper_registry

def test_database_populate_inspect_table_names(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    expected_tables = ['author', 'category', 'favourite', 'nutrition', 'recipe', 'recipe_image', 'recipe_ingredient', 'recipe_instruction', 'review', 'user']
    actual_tables = sorted(inspector.get_table_names())
    assert actual_tables == sorted(expected_tables)

def test_database_populate_select_all_users(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = 'user'

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([mapper_registry.metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        expected_users = ['thorke', 'fmercury', 'mjackson', 'william']
        assert sorted(all_users) == sorted(expected_users)

def test_database_populate_select_all_categories(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_categories_table = 'category'

    with database_engine.connect() as connection:
        # query for records in table categories
        select_statement = select([mapper_registry.metadata.tables[name_of_categories_table]])
        result = connection.execute(select_statement)

        all_categories = []
        for row in result:
            all_categories.append(row['name'])

        # Check that we have some categories
        assert len(all_categories) > 0
        # Check for some expected categories from the test data
        expected_categories = ['Frozen Desserts', 'Beverages', 'Soy/Tofu', 'Vegetable', 'Chicken', 'Pie', 'Chicken Breast', 'Dessert']
        for expected_cat in expected_categories:
            assert expected_cat in all_categories

def test_database_populate_select_all_authors(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_authors_table = 'author'

    with database_engine.connect() as connection:
        # query for records in table authors
        select_statement = select([mapper_registry.metadata.tables[name_of_authors_table]])
        result = connection.execute(select_statement)

        all_authors = []
        for row in result:
            all_authors.append(row['name'])

        # Check that we have some authors
        assert len(all_authors) > 0
        # Check for some expected authors from the test data
        expected_authors = ['Dancer', 'Stephen Little', 'Cyclopz', 'Duckie067', 'Joan Edington', 'tristitia', 'Queen Dragon Mom', 'troyh', 'Marg CaymanDesigns']
        for expected_author in expected_authors:
            assert expected_author in all_authors

def test_database_populate_select_all_recipes(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_recipes_table = 'recipe'

    with database_engine.connect() as connection:
        # query for records in table recipes
        select_statement = select([mapper_registry.metadata.tables[name_of_recipes_table]])
        result = connection.execute(select_statement)

        all_recipes = []
        for row in result:
            all_recipes.append((row['id'], row['name']))

        # Check that we have some recipes
        assert len(all_recipes) > 0
        
        # Check for some expected recipes from the test data
        expected_recipes = [
            (38, 'Low-Fat Berry Blue Frozen Dessert'),
            (40, 'Best Lemonade'),
            (41, 'Carina\'s Tofu-Vegetable Kebabs'),
            (42, 'Cabbage Soup'),
            (44, 'Warm Chicken A La King'),
            (45, 'Buttermilk Pie With Gingersnap Crumb Crust'),
            (49, 'Chicken Breasts Lombardi'),
            (52, 'Cafe Cappuccino'),
            (54, 'Carrot Cake')
        ]
        
        for expected_recipe in expected_recipes:
            assert expected_recipe in all_recipes

def test_database_populate_select_recipe_images(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_recipe_images_table = 'recipe_image'

    with database_engine.connect() as connection:
        # query for records in table recipe_images
        select_statement = select([mapper_registry.metadata.tables[name_of_recipe_images_table]])
        result = connection.execute(select_statement)

        all_images = []
        for row in result:
            all_images.append((row['recipe_id'], row['image_url'], row['position']))

        # Check that we have some recipe images
        assert len(all_images) > 0
        
        # Check that images are properly associated with recipes
        recipe_ids = set(row[0] for row in all_images)
        assert len(recipe_ids) > 0

def test_database_populate_select_recipe_ingredients(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_recipe_ingredients_table = 'recipe_ingredient'

    with database_engine.connect() as connection:
        # query for records in table recipe_ingredients
        select_statement = select([mapper_registry.metadata.tables[name_of_recipe_ingredients_table]])
        result = connection.execute(select_statement)

        all_ingredients = []
        for row in result:
            all_ingredients.append((row['recipe_id'], row['ingredient'], row['ingredient_quantity'], row['position']))

        # Check that we have some recipe ingredients
        assert len(all_ingredients) > 0
        
        # Check that ingredients are properly associated with recipes
        recipe_ids = set(row[0] for row in all_ingredients)
        assert len(recipe_ids) > 0

def test_database_populate_select_recipe_instructions(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_recipe_instructions_table = 'recipe_instruction'

    with database_engine.connect() as connection:
        # query for records in table recipe_instructions
        select_statement = select([mapper_registry.metadata.tables[name_of_recipe_instructions_table]])
        result = connection.execute(select_statement)

        all_instructions = []
        for row in result:
            all_instructions.append((row['recipe_id'], row['instruction'], row['position']))

        # Check that we have some recipe instructions
        assert len(all_instructions) > 0
        
        # Check that instructions are properly associated with recipes
        recipe_ids = set(row[0] for row in all_instructions)
        assert len(recipe_ids) > 0

def test_database_populate_select_nutrition(database_engine):

    # Get table information
    inspector = inspect(database_engine)
    name_of_nutrition_table = 'nutrition'

    with database_engine.connect() as connection:
        # query for records in table nutrition
        select_statement = select([mapper_registry.metadata.tables[name_of_nutrition_table]])
        result = connection.execute(select_statement)

        all_nutrition = []
        for row in result:
            all_nutrition.append((row['id'], row['calories'], row['fat'], row['protein']))

        # Check that we have some nutrition records
        assert len(all_nutrition) > 0
        
        # Check that nutrition values are reasonable
        for nutrition in all_nutrition:
            assert nutrition[1] > 0  # calories should be positive
            assert nutrition[2] >= 0  # fat should be non-negative
            assert nutrition[3] >= 0  # protein should be non-negative

def test_database_populate_recipe_relationships(database_engine):

    # Test that recipes are properly linked to authors, categories, and nutrition
    with database_engine.connect() as connection:
        # Query for a specific recipe with its relationships
        recipe_query = select([
            mapper_registry.metadata.tables['recipe'].c.id,
            mapper_registry.metadata.tables['recipe'].c.name,
            mapper_registry.metadata.tables['author'].c.name.label('author_name'),
            mapper_registry.metadata.tables['category'].c.name.label('category_name'),
            mapper_registry.metadata.tables['nutrition'].c.calories
        ]).select_from(
            mapper_registry.metadata.tables['recipe']
            .join(mapper_registry.metadata.tables['author'])
            .join(mapper_registry.metadata.tables['category'])
            .join(mapper_registry.metadata.tables['nutrition'])
        ).where(mapper_registry.metadata.tables['recipe'].c.id == 38)
        
        result = connection.execute(recipe_query)
        recipe_data = result.fetchone()
        
        assert recipe_data is not None
        assert recipe_data.name == 'Low-Fat Berry Blue Frozen Dessert'
        assert recipe_data.author_name == 'Dancer'
        assert recipe_data.category_name == 'Frozen Desserts'
        assert recipe_data.calories > 0

def test_database_populate_foreign_key_constraints(database_engine):

    # Test that foreign key relationships are properly established
    with database_engine.connect() as connection:
        # Check that recipe images reference valid recipes
        image_query = select([
            mapper_registry.metadata.tables['recipe_image'].c.recipe_id
        ]).where(
            mapper_registry.metadata.tables['recipe_image'].c.recipe_id.notin_(
                select([mapper_registry.metadata.tables['recipe'].c.id])
            )
        )
        
        result = connection.execute(image_query)
        orphaned_images = result.fetchall()
        assert len(orphaned_images) == 0, "Found recipe images that don't reference valid recipes"
        
        # Check that recipe ingredients reference valid recipes
        ingredient_query = select([
            mapper_registry.metadata.tables['recipe_ingredient'].c.recipe_id
        ]).where(
            mapper_registry.metadata.tables['recipe_ingredient'].c.recipe_id.notin_(
                select([mapper_registry.metadata.tables['recipe'].c.id])
            )
        )
        
        result = connection.execute(ingredient_query)
        orphaned_ingredients = result.fetchall()
        assert len(orphaned_ingredients) == 0, "Found recipe ingredients that don't reference valid recipes"

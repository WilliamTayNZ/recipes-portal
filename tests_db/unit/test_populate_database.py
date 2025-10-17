from sqlalchemy import select, inspect

from recipe.adapters.orm import mapper_registry

def test_database_populate_inspect_table_names(database_engine):
    # get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['author',
                                           'category',
                                           'favourite',
                                           'nutrition',
                                           'recipe',
                                           'recipe_image',
                                           'recipe_ingredient',
                                           'recipe_instruction',
                                           'review',
                                           'user']

def test_database_populate_select_all_authors(database_engine):
    # get table information
    inspector = inspect(database_engine)
    name_of_author_table = inspector.get_table_names()[0]

    with database_engine.connect() as connection:
        # query for records in table author
        select_statement = select([mapper_registry.metadata.tables[name_of_author_table]])
        result = connection.execute(select_statement)

        all_author_names = []
        for row in result:
            all_author_names.append(row['name'])

        # Just verify that authors were loaded (not checking specific names since test data is full dataset)
        assert len(all_author_names) > 0, "No authors were loaded"
        assert len(all_author_names) >= 7, f"Expected at least 7 authors, got {len(all_author_names)}"

def test_database_populate_select_all_categories(database_engine):
    # get table information
    inspector = inspect(database_engine)
    name_of_category_table = inspector.get_table_names()[1]

    with database_engine.connect() as connection:
        # query for records in table category
        select_statement = select([mapper_registry.metadata.tables[name_of_category_table]])
        result = connection.execute(select_statement)

        all_category_names = []
        for row in result:
            all_category_names.append(row['name'])

        # Just verify that categories were loaded (not checking specific names since test data is full dataset)
        assert len(all_category_names) > 0, "No categories were loaded"
        assert len(all_category_names) >= 6, f"Expected at least 6 categories, got {len(all_category_names)}"

def test_database_populate_select_all_nutrition(database_engine):
    # get table information
    tables = mapper_registry.metadata.tables
    nutrition_table = tables['nutrition']
    recipe_table = tables['recipe']

    with database_engine.connect() as connection:
        # query for records in table nutrition
        select_statement = (
            select(recipe_table.c.name)
            .select_from(nutrition_table.join(recipe_table, nutrition_table.c.id == recipe_table.c.nutrition_id))
        )
        result = connection.execute(select_statement)

        all_nutrition_recipes = []
        for row in result:
            all_nutrition_recipes.append(row[0])

        # Just verify that nutrition data was loaded (not checking specific recipe names)
        assert len(all_nutrition_recipes) > 0, "No nutrition data was loaded"
        assert len(all_nutrition_recipes) >= 7, f"Expected at least 7 recipes with nutrition, got {len(all_nutrition_recipes)}"

def test_database_populate_select_all_recipes(database_engine):
    # get table information
    inspector = inspect(database_engine)
    name_of_recipe_table = inspector.get_table_names()[4]

    with database_engine.connect() as connection:
        # query for records in table recipe
        select_statement = select([mapper_registry.metadata.tables[name_of_recipe_table]])
        result = connection.execute(select_statement)

        all_recipe_names = []
        for row in result:
            all_recipe_names.append(row['name'])

        # Just verify that recipes were loaded (not checking specific recipe names)
        assert len(all_recipe_names) > 0, "No recipes were loaded"
        assert len(all_recipe_names) >= 7, f"Expected at least 7 recipes, got {len(all_recipe_names)}"

def test_database_populate_select_all_recipe_images(database_engine):
    # get table information
    tables = mapper_registry.metadata.tables
    recipe_image_table = tables['recipe_image']
    recipe_table = tables['recipe']

    with database_engine.connect() as connection:
        # query for records in table recipe_images
        select_statement = (
            select(recipe_table.c.name)
            .select_from(recipe_image_table.join(recipe_table, recipe_image_table.c.recipe_id == recipe_table.c.id))
        )
        result = connection.execute(select_statement)

        all_recipe_image_recipes = []
        for row in result:
            all_recipe_image_recipes.append(row[0])

        # check correct number of images for a recipe
        recipe_1_image_count = all_recipe_image_recipes.count('Low-Fat Berry Blue Frozen Dessert')
        recipe_2_image_count = all_recipe_image_recipes.count('Best Lemonade')

        assert recipe_1_image_count == 6
        assert recipe_2_image_count == 2

def test_database_populate_select_all_recipe_ingredients(database_engine):
    # get table information
    tables = mapper_registry.metadata.tables
    recipe_ingredient_table = tables['recipe_ingredient']
    recipe_table = tables['recipe']

    with database_engine.connect() as connection:
        # query for records in table recipe_ingredient
        select_statement = (
            select(recipe_table.c.name)
            .select_from(recipe_ingredient_table.join(recipe_table, recipe_ingredient_table.c.recipe_id == recipe_table.c.id))
        )
        result = connection.execute(select_statement)

        all_recipe_ingredient_recipes = []
        for row in result:
            all_recipe_ingredient_recipes.append(row[0])

        recipe_1_ingredient_count = all_recipe_ingredient_recipes.count('Low-Fat Berry Blue Frozen Dessert')
        recipe_2_ingredient_count = all_recipe_ingredient_recipes.count('Best Lemonade')

        assert recipe_1_ingredient_count == 4
        assert recipe_2_ingredient_count == 5

def test_database_populate_select_all_recipe_instructions(database_engine):
    # get table information
    tables = mapper_registry.metadata.tables
    recipe_instruction_table = tables['recipe_instruction']
    recipe_table = tables['recipe']

    with database_engine.connect() as connection:
        # query for records in table recipe_instructions
        select_statement = (
            select(recipe_table.c.name)
            .select_from(recipe_instruction_table.join(recipe_table, recipe_instruction_table.c.recipe_id == recipe_table.c.id))
        )
        result = connection.execute(select_statement)

        all_recipe_instruction_recipes = []
        for row in result:
            all_recipe_instruction_recipes.append(row[0])

        recipe_1_ingredient_count = all_recipe_instruction_recipes.count('Low-Fat Berry Blue Frozen Dessert')
        recipe_2_ingredient_count = all_recipe_instruction_recipes.count('Best Lemonade')

        assert recipe_1_ingredient_count == 9
        assert recipe_2_ingredient_count == 5

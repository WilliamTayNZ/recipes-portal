import pytest

from recipe.adapters.database_repository import SqlAlchemyRepository


def make_repo(session_factory) -> SqlAlchemyRepository:
    return SqlAlchemyRepository(session_factory)


@pytest.mark.db
def test_search_by_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    # Pick a known recipe and derive a partial, lowercased search term from its name
    first = repo.get_first_recipe()
    assert first is not None and first.name
    term = first.name[: max(1, len(first.name) // 3)].lower()

    results = repo.get_recipes_by_name(term)
    names = {getattr(r, 'name', '').lower() for r in results}

    assert first.name.lower() in names
    # sanity : calling paginated variant should also include it when page is large enough
    page_results = repo.get_recipes_by_name_paginated(term, page=1, per_page=50)
    page_names = {getattr(r, 'name', '').lower() for r in page_results}
    assert first.name.lower() in page_names


@pytest.mark.db
def test_search_by_author_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    # Use the author of a known recipe to create a search term
    first = repo.get_first_recipe()
    assert first is not None and getattr(first, 'author', None) is not None
    author_name = getattr(first.author, 'name', '')
    assert author_name
    term = author_name[: max(1, len(author_name) // 3)].lower()

    results = repo.get_recipes_by_author_name(term)
    ids = {getattr(r, 'id', None) for r in results}
    assert first.id in ids

    # If paginated search exists, it should also find it
    if hasattr(repo, 'get_recipes_by_author_name_paginated'):
        page_results = repo.get_recipes_by_author_name_paginated(term, page=1, per_page=50)
        page_ids = {getattr(r, 'id', None) for r in page_results}
        assert first.id in page_ids


@pytest.mark.db
def test_search_by_category_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    first = repo.get_first_recipe()
    assert first is not None and getattr(first, 'category', None) is not None
    category_name = getattr(first.category, 'name', '')
    assert category_name
    term = category_name[: max(1, len(category_name) // 3)].lower()

    results = repo.get_recipes_by_category_name(term)
    ids = {getattr(r, 'id', None) for r in results}
    assert first.id in ids

    # Test paginated variant if available
    if hasattr(repo, 'get_recipes_by_category_name_paginated'):
        page_results = repo.get_recipes_by_category_name_paginated(term, page=1, per_page=50)
        page_ids = {getattr(r, 'id', None) for r in page_results}
        assert first.id in page_ids


@pytest.mark.db
def test_search_by_ingredient_name_case_insensitive_partial(session_factory):
    repo = make_repo(session_factory)

    # Ensure we have a recipe with ingredients loaded
    first = repo.get_first_recipe()
    assert first is not None
    # If no ingredients are present on this recipe, fetch another that has some using a simple scan
    candidate = first
    if not getattr(candidate, 'ingredients', None):
        # Scan a small first page; adjust if needed
        page = repo.get_recipes_paginated(page=1, per_page=25)
        for r in page:
            if getattr(r, 'ingredients', None):
                candidate = r
                break
    ings = getattr(candidate, 'ingredients', [])
    assert ings, "No ingredients found on scanned recipes; check populate() filled RecipeIngredient table."

    ing = str(ings[0])
    term = ing[: max(1, len(ing) // 3)].lower()

    results = repo.get_recipes_by_ingredient_name(term)
    ids = {getattr(r, 'id', None) for r in results}
    assert candidate.id in ids

    # Test paginated variant if available
    if hasattr(repo, 'get_recipes_by_ingredient_name_paginated'):
        page_results = repo.get_recipes_by_ingredient_name_paginated(term, page=1, per_page=50)
        page_ids = {getattr(r, 'id', None) for r in page_results}
        assert candidate.id in page_ids


import pytest
from recipe_recommendation_system.modules.semantic_search import SemanticSearch


@pytest.fixture(scope="module")
def semantic_search():
    semantic_search = SemanticSearch()
    semantic_search.run_prep_process()
    return semantic_search


def test_query_semantic_index_ingredients(semantic_search):
    query = "chicken and rice"
    result = semantic_search.query_semantic_index_recipe_titles(query=query)
    assert isinstance(result, list)

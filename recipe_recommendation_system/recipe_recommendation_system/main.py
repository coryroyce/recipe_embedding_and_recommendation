# pylint: disable=E0401

import sys

# Add the modules folder to the path to find the custom modules
sys.path.insert(0, "recipe_recommendation_system/recipe_recommendation_system/modules")
sys.path.insert(0, "recipe_recommendation_system/modules")
from modules.database_setup import DatabaseSetup
from modules.semantic_search import SemanticSearch


class InitialSetup:
    """
    Manage setting up pre-computed resources like the recipe data set and the semantic
    indices to that they do not have to be re calculated every time the code is ran.
    """

    def __init__(
        self,
    ):
        self.file_path_data: str = (
            f"recipe_recommendation_system/recipe_recommendation_system/data"
        )

    def run_prep_process(self):
        """Organize all of the main steps in the process so that the data can all be refreshed with one call"""
        # Setup the data base connection
        # db = DatabaseSetup()
        # If new data needs to be loaded from a csv, then uncomment the line below
        # db.create_data_sample_with_1000_records()

        # Example read of data:
        # Read a table by name from the database as a pandas dataframe
        # df_recipe_sample = db.read_data_as_df(table_name="recipes")
        # print(df_recipe_sample.head())

        # Semantic search
        semantic_search_instance = SemanticSearch()
        semantic_search_instance.run_prep_process()
        recipe_title_to_search = input("Type a title to search:\n")
        print("Matching recipe title:\n")
        print(
            semantic_search_instance.query_semantic_index_recipe_titles(
                query=recipe_title_to_search
            )
        )

        ingredients_to_search = input("Type an ingredient to search:\n")
        print("Matching ingredients :\n")
        print(
            semantic_search_instance.query_semantic_index_ingredients(
                query=ingredients_to_search
            )
        )

        return  # semantic_search_instance


###   Run Functions   ###
if __name__ == "__main__":
    initial_setup_instance = InitialSetup()
    initial_setup_instance.run_prep_process()

    print("Done!")

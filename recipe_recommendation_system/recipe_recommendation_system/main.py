# pylint: disable=E0401
from modules.semantic_search import SemanticSearch
from modules.database_setup import DatabaseSetup


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
        # TODO: Add the database_setup run_process here
        # TODO: Save the pre-computed semantic indexes into the semantic_search_indices folder
        print(f"Generating semantic index for recipe titles...")
        semantic_search_instance = SemanticSearch()
        initial_setup_instance.run_prep_process()

        return semantic_search_instance


###   Run Functions   ###
if __name__ == "__main__":
    initial_setup_instance = InitialSetup()
    initial_setup_instance.run_prep_process()

    print("hi")

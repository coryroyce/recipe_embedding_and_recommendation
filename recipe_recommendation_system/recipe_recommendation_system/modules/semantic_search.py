from txtai.embeddings import Embeddings
import pandas as pd
import re

# pylint: disable=E0401
from database_setup import DatabaseSetup


class SemanticSearch:
    """
    Manage all of the semantic search capabilities for ingredient and title word embeddings
    """

    def __init__(self, use_sample_ingredient_index: bool = False):
        self.df_recipe: pd.DataFrame = self.load_df_from_db(table_name="recipes")
        self.file_path_data: str = (
            f"recipe_recommendation_system/recipe_recommendation_system/data"
        )
        self.embeddings_ingredients = Embeddings(
            {"path": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"}
        )  # "sentence-transformers/nli-mpnet-base-v2"
        self.embeddings_recipe_titles = Embeddings(
            {"path": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"}
        )
        self.top_k_matches_ingredients: int = 5
        self.top_k_matches_recipe_titles: int = 5
        self.file_path_substitutions_ground_truth: str = (
            f"{self.file_path_data}/df_ingredient_substitutions_ground_truth.csv"
        )
        self.df_ingredient_substitutions_ground_truth: pd.DataFrame = pd.DataFrame()
        self.df_unique_ingredients: pd.DataFrame = pd.DataFrame()
        self.use_sample_ingredient_index: bool = use_sample_ingredient_index

    def run_prep_process(self):
        """Organize all of the main steps in the process so that the data can all be refreshed with one call"""
        # Update the txtai index for all of the recipe titles
        print(f"Generating semantic index for recipe titles...")
        self.create_semantic_search_index_recipe_titles()

        ### Create ingredients based semantic search ###
        # Load the ground truth ingredient substitution dataframe
        print(f"Gathering list of unique ingredients...")
        self.create_df_ingredient_substitutions_ground_truth()

        # Create unique list of possible ingredient substitutes
        self.generate_unique_ingredients_df()

        # Update the txtai index for all of the ingredients
        print(f"Generating semantic index for ingredients...")
        self.create_semantic_search_index_ingredients()

        print(f"Preparation Process Complete!!!")

        return

    def create_semantic_search_index_recipe_titles(self):
        """Use the recipe dataframe to create a semantic search index"""
        # Create a list of unique ingredients in the correct tuple format for txtai embeddings to create an index
        list_of_recipe_titles = [
            (index, row["title"], None) for index, row in self.df_recipe.iterrows()
        ]

        # Create and update the index for the embedding based in the unique ingredients
        self.embeddings_recipe_titles.index(list_of_recipe_titles)

        return

    def query_semantic_index_recipe_titles(self, query: str) -> list:
        """Run a query through the semantic search index and return top k responses"""
        # Matches shape is [(index,score), ...] e.g [(0, 0.4172574281692505), (3, 0.3305395245552063)]
        matches: list = self.embeddings_recipe_titles.search(
            query, self.top_k_matches_recipe_titles
        )

        # Get just the indices from the matches
        matching_indices = [tup[0] for tup in matches]

        # Get the ingredient associated with the each index
        top_k_matching_recipe_titles = self.df_recipe.iloc[matching_indices][
            "title"
        ].tolist()

        return top_k_matching_recipe_titles

    def create_df_ingredient_substitutions_ground_truth(self):
        """Load in the ground truth data frame"""
        # Load in the ingredients ground truth from a csv
        df = self.load_df_from_db(table_name="ingredient_substitutions_ground_truth")

        # Clean the ground truth dataframe
        # Split each string into a list
        df["substitutes"] = df["substitutes"].apply(lambda x: x.split(","))

        # Clean each ingredient in the list
        df["substitutes"] = df["substitutes"].apply(
            lambda x: [self.clean_ingredient_substitution(item) for item in x]
        )

        # Update the dataframe
        self.df_ingredient_substitutions_ground_truth = df.copy()

        return df

    @staticmethod
    def clean_ingredient_substitution(ingredient: str):
        """Clean the ingredient string in a consistent manner"""
        ingredient_clean = ingredient
        # Make the string lower case
        ingredient_clean = (
            ingredient_clean.lower()
        )  # .replace("[/+/_/*]", " ", regex=True).replace("\s+", " ", regex=True).strip()
        # Remove special symbols
        ingredient_clean = re.sub(r"[/+/_/*]", " ", ingredient_clean)
        # remove extra spaces
        ingredient_clean = re.sub(r"\s+", " ", ingredient_clean).strip()

        return ingredient_clean

    def generate_unique_ingredients_df(self):
        "Create unique list of possible substitutes to choose from"
        df = self.df_ingredient_substitutions_ground_truth.copy()

        # Get all of the unique values from the substitutes column
        unique_values = df["substitutes"].explode().unique()
        df_unique_ingredients = pd.DataFrame({"ingredient_substitutes": unique_values})

        # Remove leading and trailing white space
        df_unique_ingredients["ingredient_substitutes"] = df_unique_ingredients[
            "ingredient_substitutes"
        ].str.strip()

        # Drop the row with a whitespace character
        df_unique_ingredients = df_unique_ingredients[
            ~df_unique_ingredients["ingredient_substitutes"].str.isspace()
        ]

        # Drop rows with null values
        df_unique_ingredients.replace({"": None, " ": None}, inplace=True)
        df_unique_ingredients = df_unique_ingredients.dropna()

        # Drop rows with duplicates
        df_unique_ingredients.drop_duplicates(inplace=True)

        # Sort the ingredient substitutes
        df_unique_ingredients = df_unique_ingredients.sort_values(
            by="ingredient_substitutes"
        ).reset_index(drop=True)

        # Check if using a smaller sample index for dev (full index takes ~5 min)
        if self.use_sample_ingredient_index:
            df_unique_ingredients = df_unique_ingredients.head(20)

        # Update the class instance of this dataframe
        self.df_unique_ingredients = df_unique_ingredients

        return df_unique_ingredients

    def create_semantic_search_index_ingredients(self):
        """Use the dataframe of unique ingredients to create a semantic search index"""
        # Create a list of unique ingredients in the correct tuple format for txtai embeddings to create an index
        list_of_unique_ingredients = [
            (index, row["ingredient_substitutes"], None)
            for index, row in self.df_unique_ingredients.iterrows()
        ]

        # Create and update the index for the embedding based in the unique ingredients
        self.embeddings_ingredients.index(list_of_unique_ingredients)

        return

    def query_semantic_index_ingredients(self, query: str, top_k: int = None) -> list:
        """Run a query through the semantic search index and return top k responses"""
        # Check if a top_k value was provide if not use default specified in class instance
        if top_k is None:
            top_k = self.top_k_matches_ingredients

        # Matches shape is [(index,score), ...] e.g [(0, 0.4172574281692505), (3, 0.3305395245552063)]
        matches: list = self.embeddings_ingredients.search(query, top_k + 1)

        # Get just the indices from the matches
        matching_indices = [tup[0] for tup in matches]

        # Get the ingredient associated with the each index
        top_k_matching_ingredients = self.df_unique_ingredients.iloc[matching_indices][
            "ingredient_substitutes"
        ].tolist()

        # If the input is an exact match then remove is since that is not a substitution
        if query in top_k_matching_ingredients:
            top_k_matching_ingredients.remove(query)

        # Make sure that only the first 5 matches are returned (may have 6 if there is not an exact match)
        top_k_matching_ingredients = top_k_matching_ingredients[:top_k]

        return top_k_matching_ingredients

    @staticmethod
    def save_semantic_search_index(embedding: Embeddings, embedding_name_to_save: str):
        """Save a pre-computed semantic search index to avoid re-generation"""
        # Save the embedding to the current directory
        embedding.save(
            f"./recipe_recommendation_system/recipe_recommendation_system/semantic_search_indices/{embedding_name_to_save}.tar.gz"
        )

        return

    @staticmethod
    def load_semantic_search_index(embedding: Embeddings, embedding_name_to_load: str):
        """Save a pre-computed semantic search index to avoid re-generation"""
        # Save the embedding to the current directory
        # temp_embedding =
        embedding.load(
            f"./recipe_recommendation_system/recipe_recommendation_system/semantic_search_indices/{embedding_name_to_load}.tar.gz"
        )

        return  # temp_embedding

    def load_df_from_db(self, table_name: str):
        """Load in a dataframe of the recipes from the sql database"""
        db = DatabaseSetup()
        df = db.read_data_as_df(table_name=table_name)

        return df


###   Run Functions   ###
if __name__ == "__main__":
    # # Instantiate the database instance/connection
    semantic_search = SemanticSearch()
    # semantic_search.run_prep_process()
    # print(semantic_search.query_semantic_index_recipe_titles(query="pork"))
    # semantic_search.save_semantic_search_index(
    #     embedding=semantic_search.embeddings_ingredients,
    #     embedding_name_to_save="embeddings_ingredients",
    # )
    # semantic_search.save_semantic_search_index(
    #     embedding=semantic_search.embeddings_recipe_titles,
    #     embedding_name_to_save="embeddings_recipe_titles",
    # )

    # Update semantic search index from pre-calculated index
    # semantic_search.embeddings_recipe_titles = (
    semantic_search.load_semantic_search_index(
        embedding=semantic_search.embeddings_recipe_titles,
        embedding_name_to_load="embeddings_recipe_titles",
    )

    print(semantic_search.query_semantic_index_recipe_titles(query="pork"))

    print("hi")
    # self.embeddings_recipe_titles

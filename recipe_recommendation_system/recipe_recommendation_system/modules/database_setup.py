import sqlite3
import pandas as pd


class DatabaseSetup:
    """
    Database class for creating and reading SQLite data
    """

    def __init__(self):
        self.file_path_data: str = (
            f"recipe_recommendation_system/recipe_recommendation_system/data"
        )
        self.db_name: str = f"recipe_database.db"
        self.connection = sqlite3.connect(
            database=f"{self.file_path_data}/{self.db_name}", check_same_thread=False
        )
        self.cursor = self.connection.cursor()
        self.use_sample_db: bool = True

    def __del__(self):
        self.connection.close()

    def run_prep_process(self):
        """Create all tables and SQLite database if it doesn't exist yet"""
        print(f"Creating recipes table...")
        self.create_recipe_data_table()

        print(f"Creating ingredient substitution ground truth table...")
        self.create_ingredient_substitutions_ground_truth_table()

        print(f"Preparation Process Complete!!!")

        return

    def create_recipe_data_table(self):
        """Load data from a csv"""
        # Choose to load the sample data set or the full dataset
        if self.use_sample_db is True:
            file_name_recipe_csv = "recipe_data_1000.csv"
        else:
            file_name_recipe_csv = "recipe_data.csv"  # This needs to be updated based on the final data we use

        # Add the name to the file path
        file_path_recipe_csv = f"{self.file_path_data}/{file_name_recipe_csv}"

        # Read specific columns of csv file using Pandas
        df = pd.read_csv(
            file_path_recipe_csv,
            usecols=["title", "ingredients", "directions", "NER"],
        )

        # Update the column names
        columns_dict = {
            "title": "title",
            "ingredients": "ingredients_with_measurements",
            "directions": "directions",
            "NER": "ingredients",
        }

        df = df.rename(columns=columns_dict)

        # Create the table in SQLite database
        table_name = "recipes"
        # query = f"CREATE TABLE IF NOT EXISTS {table_name} (title, ingredients_with_measurements, directions, ingredients)"
        df.to_sql(table_name, self.connection, if_exists="replace", index=True)
        self.connection.commit()

        return

    def create_ingredient_substitutions_ground_truth_table(self):
        """Load data from a csv"""
        # Add the name to the file path
        file_path_ingredient_substitutions_ground_truth_csv = (
            f"{self.file_path_data}/df_ingredient_substitutions_ground_truth.csv"
        )

        # Read specific columns of csv file using Pandas
        df = pd.read_csv(
            file_path_ingredient_substitutions_ground_truth_csv,
            usecols=["ingredient", "substitutes"],
        )

        # Create the table in SQLite database
        table_name = "ingredient_substitutions_ground_truth"
        df.to_sql(table_name, self.connection, if_exists="replace", index=True)
        self.connection.commit()
        return

    def read_data_as_df(self, table_name: str):
        """Read in the table as a Pandas Dataframe"""
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connection)
        self.connection.close()
        return df


###   Run Functions   ###
if __name__ == "__main__":
    # Instantiate the database instance/connection
    db = DatabaseSetup()

    # Create tables
    # db.run_prep_process()

    # Read a table by name from the database as a pandas dataframe
    df_recipe_sample = db.read_data_as_df(table_name="recipes")
    print(df_recipe_sample.head())

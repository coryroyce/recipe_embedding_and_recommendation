import pandas as pd


class DataPrep:
    """
    Prepare data for analysis
    """

    def __init__(
        self,
        local_file_path_to_full_1m_recipe_data: str = f"/Users/coryrandolph/Downloads/full_dataset.csv",
    ):
        self.local_file_path_to_full_1m_recipe_data: str = (
            local_file_path_to_full_1m_recipe_data
        )

    def create_data_sample_with_1000_records(self):
        """
        Loads in the full 1 million recipe dataset and then creates a .csv file with the
        top 1,000 rows/recipes

        Args:
            file_path (str, optional): Local file path where the full dataset lives. Defaults to "/Users/coryrandolph/Downloads/dataset/full_dataset.csv".

        Returns:
            str: Success message
        """
        # Load in full dataset
        df = pd.read_csv(self.local_file_path_to_full_1m_recipe_data)

        # Rename index file
        df.rename(columns={"Unnamed: 0": "id"}, inplace=True)

        # Keep just the first 1,000 rows
        df_reduced = df.sample(n=1_000, random_state=3)
        print(df_reduced.head())
        df_reduced.to_csv(
            "./development/data_prep/data/recipe_data_1000.csv", index=False
        )
        # Uncomment to export the standard dataset name
        # df_reduced.to_csv(
        #     "./development/data_prep/data/recipe_data.csv", index=False
        # )

        return f"Data sample of 1,000 sample create successfully"


###   Run Functions   ###
if __name__ == "__main__":
    # Instantiate class and method to be run
    data_prep = DataPrep()
    data_prep.create_data_sample_with_1000_records()
    # print("hi")

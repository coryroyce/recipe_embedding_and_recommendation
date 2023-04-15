# Recipe Embedding and Recommendation

## Goal

Develop a recommendation system for recipes based on similar ingredients. Apply embedding models to encode text  based ingredients into numerical values in order to calculate similarity and content based recommendations.

## Setup

1. Clone this repository locally
1. Run Flask app to run locally

### Modify Sample Dataset (Optional Dev)

1. Update the SQLite database to a different dataset
    * Modify the function to select desired subset of 1M RecipeNLG dataset (default is 1,000 random recipes)
    * File to change data: development/data_prep/data_prep.py
    * Uncomment the code for exporting the recipe_data.csv
    * Run this file directly
1. Load new data into the SQLiteDatabase
    * Modify the database_setup.py file to run the prep process at the bottom of the file
    * File to change: recipe_recommendation_system/recipe_recommendation_system/modules/database_setup.py
    * Run this file directly
1. Recompute Semantic Search Indices
    * The semantic search index for recipe titles needs to be recomputed based on the new recipe dataset
    * Uncomment line ~273 `# semantic_search.recalculate_all_semantic_search_indices()`
    * recipe_recommendation_system/recipe_recommendation_system/modules/semantic_search.py
    * Run this file directly

## Reference

Primary Dataset [RecipeNLG dataset](https://recipenlg.cs.put.poznan.pl/dataset)

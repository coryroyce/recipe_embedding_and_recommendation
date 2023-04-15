# Recipe Embedding and Recommendation

## Goal

Develop a recommendation system for recipes based on similar ingredients. Apply embedding models to encode text  based ingredients into numerical values in order to calculate similarity and content based recommendations.

## Setup

Note that this repo uses [Poetry](https://python-poetry.org/docs/) to manage the packages
1. Clone this repo
    * `git clone https://github.com/coryroyce/recipe_embedding_and_recommendation.git`
1. Install [Poetry](https://python-poetry.org/docs/) if needed
1. Change directory into the "recipe_recommendation_system" subfolder
    * `cd recipe_recommendation_system`
1. Run `poetry install` to load all of the needed python packages and create a virtual environnement.
1. Activate the virtual environment
    * `source .venv/bin/activate`
1. Run Flask app to run locally
    * `python -m flask --app app run`
    * Click the link to the local port and interact with the demo

## Architecture

1. Flask Application
1. Recipe Dataset
1. NER extraction of ingredients
1. Semantic Search Embeddings for Recipes and Ingredients


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

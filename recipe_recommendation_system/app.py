import os, base64, re
import argparse
import json
import sqlite3
from flask import Flask, render_template, request
import spacy

from recipe_recommendation_system.modules.semantic_search import SemanticSearch

# handle input arguments
parser = argparse.ArgumentParser(description='Recipe Recommendation Application')

parser.add_argument('-d', '--debug', action='store_true', help='Run in debug')
parser.add_argument('-g', '--gpu', action='store_true', help='Run with GPU-trained model')

args = parser.parse_args()

# initialize flask app
app = Flask(__name__)

# initialize semantic search instance
ingredient_embedding = SemanticSearch()
ingredient_embedding.run_prep_process()

# initialize spacy model
if args.gpu:
    spacy.prefer_gpu()
    nlp = spacy.load('./recipe_recommendation_system/recipe_recommendation_system/data/recipeNER_GPU')
else:
    nlp = spacy.load('./recipe_recommendation_system/recipe_recommendation_system/data/recipeNER')

# set current query to blank for search page
cur_query = ""


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Provide endpoint for the main page of the application - the recipe search page
    """
    if request.method == "POST":
        # search query has been posted
        data = dict(request.form)
        indices = ingredient_embedding.query_semantic_index_recipe_titles(
            query=data["search"]
        )
        results = ingredient_embedding.df_recipe.iloc[indices]["title"].tolist()
        cur_query = data["search"]
    else:
        cur_query = ""
        results = []
        indices = []
    return render_template(
        "index.html", recipes=results, cur_query=cur_query, indices=indices
    )


@app.route("/recipes/<int:index>")
def show_recipe(index):
    """
    Provide endpoint for recipe page - gives ingredients, directions, and provides substitutions
    """
    recipe = ingredient_embedding.df_recipe.iloc[index]
    title = recipe["title"]
    directions = "\n".join(json.loads(recipe["directions"]))
    ingredient_list = json.loads(recipe["ingredients_with_measurements"])
    ingredients = "\n".join(ingredient_list)

    docs = [nlp(ing) for ing in ingredient_list]
    ingredient_ents = [str(ent) for doc in docs for ent in doc.ents]
    print(ingredient_ents)

    sub_ingredients = lambda q: ingredient_embedding.query_semantic_index_ingredients(
        query=q
    )
    data = {ent: sub_ingredients(ent) for ent in ingredient_ents}

    ingredient_ents = sorted(ingredient_ents, key=len, reverse=True)
    for ent in ingredient_ents:
        ingredients = re.sub(
            r'(?<!>){}(?!<)'.format(re.escape(ent)), 
            f'<span class="highlighted-word bg-primary text-light">{ent}</span>',
            ingredients)

    data_str = json.dumps(data)

    return render_template(
        "recipe.html",
        title=title,
        directions=directions,
        ingredients=ingredients,
        subs=data_str,
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    Provide endpoint to simply query the database
    """
    if request.method == "POST":
        data = dict(request.form)
        recipes = get_recipe_by_title(data["search"])
    else:
        recipes = []
    return render_template("search.html", recipes=recipes)


def get_recipe_by_title(query):
    """
    Function to query the database
    """
    conn = sqlite3.connect(
        "recipe_recommendation_system/recipe_recommendation_system/data/recipe_database.db"
    )
    conn.row_factory = sqlite3.Row
    clean = query.replace("'", "''")
    result = conn.execute(f"SELECT * FROM recipes WHERE title = '{clean}'").fetchall()
    conn.close()
    return result


if __name__ == "__main__":
    app.run(debug=args.debug)

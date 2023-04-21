import os, base64, re
import json
import sqlite3
from flask import Flask, render_template, request
import spacy

from recipe_recommendation_system.modules.semantic_search import SemanticSearch

app = Flask(__name__)

ingredient_embedding = SemanticSearch()
ingredient_embedding.run_prep_process()

spacy.prefer_gpu()
nlp = spacy.load('./recipe_recommendation_system/recipe_recommendation_system/data/recipeNER')

cur_query = ""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
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

    for ent in data.keys():
        ingredients = ingredients.replace(
            ent, f'<span class="highlighted-word bg-primary text-light">{ent}</span>')

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
    if request.method == "POST":
        data = dict(request.form)
        recipes = get_recipe_by_title(data["search"])
    else:
        recipes = []
    return render_template("search.html", recipes=recipes)


def get_recipe_by_title(query):
    conn = sqlite3.connect(
        "recipe_recommendation_system/recipe_recommendation_system/data/recipe_database.db"
    )
    conn.row_factory = sqlite3.Row
    clean = query.replace("'", "''")
    result = conn.execute(f"SELECT * FROM recipes WHERE title = '{clean}'").fetchall()
    conn.close()
    return result


if __name__ == "__main__":
    app.run(debug=True)

import os, base64
import json
import sqlite3
from flask import Flask, render_template, request

from recipe_recommendation_system.modules.semantic_search import SemanticSearch

app = Flask(__name__)

ingredient_embedding = SemanticSearch()
ingredient_embedding.run_prep_process()

cur_query = ''

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = dict(request.form)
        results = ingredient_embedding.query_semantic_index_recipe_titles(query=data['search'])
        cur_query = data['search']
    else:
        cur_query = ''
        results = []
    return render_template('index.html', recipes=results, cur_query=cur_query)


@app.route('/recipes/<int:index>')
def show_recipe(index):
    recipe = ingredient_embedding.df_recipe.iloc[index]
    print(recipe)


@app.route('/search', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = dict(request.form)
        recipes = get_recipe_by_title(data['search'])
    else:
        recipes = []
    return render_template('search.html', recipes=recipes)



def get_recipe_by_title(query):
    conn = sqlite3.connect('recipe_recommendation_system/recipe_recommendation_system/data/recipe_database.db')
    conn.row_factory = sqlite3.Row
    clean = query.replace("'", "''")
    result = conn.execute(f"SELECT * FROM recipes WHERE title = '{clean}'").fetchall()
    conn.close()
    return result


if __name__ == "__main__":
    app.run(debug=True)
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
def index():
    if request.method == 'POST':
        data = dict(request.form)
        indices = ingredient_embedding.query_semantic_index_recipe_titles(query=data['search'])
        results = ingredient_embedding.df_recipe.iloc[indices]['title'].tolist()
        cur_query = data['search']
    else:
        cur_query = ''
        results = []
        indices = []
    return render_template('index.html', recipes=results, cur_query=cur_query, indices=indices)


@app.route('/recipes/<int:index>')
def show_recipe(index):
    recipe = ingredient_embedding.df_recipe.iloc[index]
    title = recipe['title']
    directions = '\n'.join(json.loads(recipe['directions']))
    ingredients = '\n'.join(json.loads(recipe['ingredients_with_measurements']))
    ingredient_ents = json.loads(recipe['ingredients'])

    sub_ingredients = lambda q: ingredient_embedding.query_semantic_index_ingredients(query=q)
    data = {ent: sub_ingredients(ent) for ent in ingredient_ents}
    data_str = json.dumps(data, indent=4)
    
    return render_template('recipe.html', title=title, directions=directions, ingredients=ingredients, subs=data_str)



@app.route('/search', methods=['GET', 'POST'])
def search():
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
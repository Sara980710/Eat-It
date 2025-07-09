# Recipe & Shopping List Starter Project (Flask)

A minimal, self‑contained web app written in **Python 3 + Flask + SQLite** that lets you:

* Add / view **recipes** with ingredients
* Click once to add a recipe’s ingredients to a **shopping list**
* Check items off the shopping list

➡️ Ideal as a learning scaffold—you can run it locally in minutes and extend at your own pace.

---

## 📁 Directory structure

```
.
├── app.py                # Flask application + routes
├── models.py             # SQLAlchemy ORM models
├── requirements.txt      # Runtime dependencies
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── recipes.html
│   └── shopping_list.html
├── static/               # Front‑end JS & CSS
│   ├── app.js
│   └── styles.css
└── README.md             # Setup instructions
```

---

## ⚡ Quick‑start

```bash
# 1.  Set up Python venv (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2.  Install dependencies
pip install -r requirements.txt

# 3.  Initialise the SQLite database
ython -m flask --app app init-db

# 4.  Run the dev server
flask --app app run --debug  # Open http://127.0.0.1:5000
```

---

## 🔑 Environment variables (optional)

If you’d like to point at a different DB file or run in production, set:

* `FLASK_ENV=production`
* `DATABASE_URL=sqlite:///absolute/path/to/your.db` (or any SQLAlchemy‑compatible URL)

---

## 🐍 requirements.txt

```text
Flask==3.0.0
Flask-SQLAlchemy==3.0.4
```

---

## 🗃️ models.py

```python
"""Database models & relationships."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )

class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(30))

    recipe = db.relationship("Recipe", back_populates="ingredients")
    ingredient = db.relationship("Ingredient")

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredient.id"), nullable=False)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(30))
    is_checked = db.Column(db.Boolean, default=False)

    ingredient = db.relationship("Ingredient")
```

---

## 🚀 app.py

```python
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Ingredient, Recipe, RecipeIngredient, ShoppingItem

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shopping.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # CLI helper to bootstrap the DB
    @app.cli.command("init-db")
    def init_db():
        """Create tables (flask --app app init-db)."""
        with app.app_context():
            db.create_all()
        print("📦  Database initialised → shopping.db")

    @app.route("/")
    def index():
        return redirect(url_for("recipe_list"))

    # ────────────────────────── Recipe routes ──────────────────────────
    @app.route("/recipes")
    def recipe_list():
        recipes = Recipe.query.all()
        return render_template("recipes.html", recipes=recipes)

    @app.route("/recipes", methods=["POST"])
    def recipe_add():
        data = request.json  # {name, description, ingredients:[{name,quantity,unit}]}
        recipe = Recipe(name=data["name"], description=data.get("description"))
        for ing in data["ingredients"]:
            ingredient = Ingredient.query.filter_by(name=ing["name"]).first()
            if not ingredient:
                ingredient = Ingredient(name=ing["name"])
            ri = RecipeIngredient(
                ingredient=ingredient,
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
            )
            recipe.ingredients.append(ri)
        db.session.add(recipe)
        db.session.commit()
        return jsonify({"status": "ok", "id": recipe.id}), 201

    # ─────────────────────── Shopping list routes ───────────────────────
    @app.route("/shopping-list")
    def shopping_list():
        items = ShoppingItem.query.all()
        return render_template("shopping_list.html", items=items)

    @app.route("/shopping-list/add-from-recipe/<int:recipe_id>", methods=["POST"])
    def add_from_recipe(recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        for ri in recipe.ingredients:
            db.session.add(
                ShoppingItem(
                    ingredient=ri.ingredient,
                    quantity=ri.quantity,
                    unit=ri.unit,
                )
            )
        db.session.commit()
        return jsonify({"status": "added"})

    @app.route("/shopping-list/check/<int:item_id>", methods=["POST"])
    def toggle_item(item_id):
        item = ShoppingItem.query.get_or_404(item_id)
        item.is_checked = not item.is_checked
        db.session.commit()
        return jsonify({"checked": item.is_checked})

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
```

---

## 🎨 templates/base.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Recipes & Shopping List</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}" />
  </head>
  <body>
    <header>
      <nav>
        <a href="{{ url_for('recipe_list') }}">Recipes</a> |
        <a href="{{ url_for('shopping_list') }}">Shopping List</a>
      </nav>
    </header>
    <main>
      {% block content %}{% endblock %}
    </main>
    <script src="{{ url_for('static', filename='app.js') }}"></script>
  </body>
</html>
```

---

## templates/recipes.html

```html
{% extends 'base.html' %}
{% block content %}
<h1>Recipes</h1>
<ul>
  {% for recipe in recipes %}
    <li>
      <strong>{{ recipe.name }}</strong>
      <button onclick="addToShopping({{ recipe.id }})">Add ingredients to shopping list</button>
    </li>
  {% endfor %}
</ul>
{% endblock %}
```

---

## templates/shopping\_list.html

```html
{% extends 'base.html' %}
{% block content %}
<h1>Shopping List</h1>
<ul>
  {% for item in items %}
    <li>
      <input type="checkbox" onchange="toggleCheck({{ item.id }})" {% if item.is_checked %}checked{% endif %} />
      {{ item.quantity or '' }} {{ item.unit or '' }} {{ item.ingredient.name }}
    </li>
  {% endfor %}
</ul>
{% endblock %}
```

---

## 📜 static/app.js

```javascript
function addToShopping(recipeId) {
  fetch(`/shopping-list/add-from-recipe/${recipeId}`, { method: 'POST' })
    .then(() => (window.location.href = '/shopping-list'));
}

function toggleCheck(itemId) {
  fetch(`/shopping-list/check/${itemId}`, { method: 'POST' })
    .then(() => window.location.reload());
}
```

---

## 💅 static/styles.css

```css
body {
  font-family: system-ui, sans-serif;
  margin: 0 auto;
  max-width: 42rem;
  padding: 2rem;
}
header nav a {
  margin-right: .5rem;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  margin: .5rem 0;
}
button {
  margin-left: 1rem;
}
```

---

## 📖 README.md (excerpt)

This starter covers the **minimum viable product** only. Consider adding:

* User authentication (Flask‑Login)
* Better UI (React, Vue, or Bootstrap)
* Drag‑and‑drop recipe re‑ordering, persistent item checked‑state, etc.

---

### Next steps

* 🍰 Bake tests with **pytest + Flask‑Testing**.
* 🌈 Swap SQLite for PostgreSQL when deploying.
* 🚢 Dockerise the stack (Dockerfile + docker‑compose.yml).

Happy cooking & coding! 👩‍🍳👨‍🍳

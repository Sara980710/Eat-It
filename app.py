from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Ingredient, Recipe, RecipeIngredient, ShoppingItem
import os

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") + "?sslmode=require"
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

    @app.route("/recipes/new", methods=["GET"])
    def recipe_new():
        return render_template("recipe_form.html")

    @app.route("/recipes/new", methods=["POST"])
    def recipe_create():
        name = request.form.get("name")
        description = request.form.get("description")
        ingredients_json = request.form.get("ingredients_json", "[]")
        import json
        ingredients = json.loads(ingredients_json)

        recipe = Recipe(name=name, description=description)
        for ing in ingredients:
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
        return redirect(url_for("recipe_list"))

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

    @app.route("/shopping-list/clear-checked", methods=["POST"])
    def clear_checked_items():
        ShoppingItem.query.filter_by(is_checked=True).delete()
        db.session.commit()
        return jsonify({"status": "cleared"})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)     # unchanged, now uses the variable above
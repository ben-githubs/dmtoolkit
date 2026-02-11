"""Additional pages!"""
from dataclasses import asdict
import json

from flask import Blueprint, abort, render_template, request

from dmtoolkit.api.items import get_item
from dmtoolkit.modules.kibbles.loot import Locales, gather, get_gathering_variant, ItemWrapper
from dmtoolkit.modules.kibbles.crafting import list_recipes, get_recipe

kibbles_bp = Blueprint(
    "kibbles",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/kibbles/static",
    url_prefix = "/kibbles"
)

@kibbles_bp.route("/gathering", methods=["GET"])
def gathering():
    page = {
        "title": "Gathering Ingredients"
    }
    return render_template("gathering.jinja2", page=page, locales=Locales, loot_response=None, default_locale="")

@kibbles_bp.route("/gathering/<locale_name>", methods=["GET"])
def roll_gathering(locale_name: str):
    locale = Locales(locale_name)
    results = gather(locale)
    page = {
        "title": "Gathering Ingredients"
    }
    results.items =[
        ItemWrapper(get_gathering_variant(locale, item_wrapper.item), item_wrapper.quantity) for item_wrapper in results.items
    ]
    return render_template("gathering.jinja2", page=page, locales=Locales, loot_response=results, default_locale=locale)

@kibbles_bp.route("/crafting", methods=["GET"])
def crafting_view():
    page = {
        "title": "Crafting"
    }
    recipes = list_recipes()
    return render_template("crafting.jinja2", page=page, items=recipes.keys())

@kibbles_bp.route("/crafting/recipe")
def get_crafting_recipe_view():
    item_id = request.args.get("item_id", "")
    item = get_item(item_id)
    if not item:
        return f"No item named {item_id}", 404
    
    return render_template("_recipe.jinja2", item=item, recipes=get_recipe(item))
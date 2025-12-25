"""Additional pages!"""
from dataclasses import asdict
import json

from flask import Blueprint, render_template

from dmtoolkit.modules.kibbles.loot import Locales, gather, get_gathering_variant, ItemWrapper

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

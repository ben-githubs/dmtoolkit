import json

from flask import Blueprint, render_template, redirect, url_for

from dmtoolkit.api.players import list_players, create_player, get_player, update_player
from dmtoolkit.players.forms import CreateForm, UpdateForm

players_bp = Blueprint(
    "players_bp",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/players/static",
    url_prefix = "/players"
)

@players_bp.route("/list")
def list_players_page():
    page = {
        "title": "DMTTools - Players"
    }
    players = list_players()
    return render_template("list_players.jinja2", page=page, players=players)


@players_bp.route("/new", methods=["GET", "POST"])
def new_player_page():
    form = CreateForm()
    if form.validate_on_submit():
        player = {
            "name": form.name.data,
            "ac": form.ac.data,
            "pp": form.pp.data,
            "hp": form.hp.data
        }
        create_player(**player)
        return redirect(url_for("players_bp.list_players_page"))
    
    page = {
        "title": "DMTools - New Player"
    }
    return render_template("new_player.jinja2", page=page, form=form)


@players_bp.route("/edit/<player_name>", methods=["GET","POST"])
def update_player_page(player_name: str):
    form = UpdateForm()
    player = get_player(player_name)
    if not player:
        return "404 Player Not Found"
    if form.validate_on_submit():
        player_params = {}
        if val := form.name.data:
            player_params["name"] = val
        if val := form.ac.data:
            player_params["ac"] = val
        if val := form.hp.data:
            player_params["hp"] = val
        if val := form.pp.data:
            player_params["pp"] = val
        update_player(player_name, **player_params)
        return redirect(url_for("players_bp.list_players_page"))
    
    page = {
        "title": f"DMTools - Edit {player_name}"
    }
    return render_template("edit_player.jinja2", page=page, player=player, form=form)
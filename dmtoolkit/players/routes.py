from dataclasses import asdict
import json

from flask import Blueprint, render_template, redirect, url_for, request, Response, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from dmtoolkit.api.players import Player

players_bp = Blueprint(
    "players_bp",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/players/static",
    url_prefix = "/players"
)

class CreateForm(FlaskForm):
    name = StringField("Name", [DataRequired()])
    ac = IntegerField("AC", [DataRequired()])
    hp = IntegerField("Max HP", [DataRequired()])
    pp = IntegerField("Passive Perception", [DataRequired()])
    submit = SubmitField("Create Player Character")

    def validate_name(self, field):
        players = _load_players()
        if any(field.data == p.name for p in players):
            raise ValidationError(f"Cannot create new player with name '{field.data}' because that name is already in use.")



def UpdateForm():
    form = CreateForm()
    form.name.validators = ()
    form.ac.validators = ()
    form.hp.validators = ()
    form.pp.validators = ()
    form.submit.label.text = "Update Player"
    return form

@players_bp.route("/list")
def list_players_page():
    page = {
        "title": "DMTTools - Players"
    }
    players = _load_players()
    return render_template("list_players.jinja2", page=page, players=players)


@players_bp.route("/new", methods=["GET", "POST"])
def new_player_page():
    players = _load_players()
    form = CreateForm()
    def validate_name(_, field):
        print("I AM CALLED")
        if any(field.data == p.name for p in players):
            raise ValueError(f"Cannot create new player with name '{new_player.name}' because that name is already in use.")
    setattr(form, "validate_name", validate_name)
    if form.validate_on_submit():
        player = {
            "name": form.name.data,
            "ac": form.ac.data,
            "pp": form.pp.data,
            "hp": form.hp.data
        }
        new_player = (Player(**player))
        players.append(new_player)
        resp = make_response(redirect(url_for("players_bp.list_players_page")))
        _save_players(resp, players)
        return resp
    
    page = {
        "title": "DMTools - New Player"
    }
    return render_template("new_player.jinja2", page=page, form=form)


@players_bp.route("/edit/<player_name>", methods=["GET","POST"])
def update_player_page(player_name: str):
    form = UpdateForm()
    players = _load_players()
    player_arr = [p for p in players if p.name == player_name]
    if not player_arr:
        return "404 Player Not Found"
    player = player_arr[0]
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

        player_dict = asdict(player)
        player_dict |= player_params # Update player params
        new_player = Player(**player_dict)
        if new_player.name != player.name and any(p.name == new_player.name for p in players):
            # TODO: Handle this more gracefully
            raise ValueError(f"Cannot rename player to '{new_player.name}' as this name is already in use")
        idx = players.index(player)
        players[idx] = new_player

        resp = make_response(redirect(url_for("players_bp.list_players_page")))
        _save_players(resp, players)
        return resp
    
    page = {
        "title": f"DMTools - Edit {player_name}"
    }
    return render_template("edit_player.jinja2", page=page, player=player, form=form)

@players_bp.route("/delete/<player_name>", methods=["GET"])
def delete_player(player_name: str):
    players = _load_players()
    new_players = [p for p in players if p.name != player_name]
    resp = make_response(redirect(url_for("players_bp.list_players_page")))
    _save_players(resp, new_players)
    return resp

def _load_players() -> list[Player]:
    player_specs = json.loads(request.cookies.get("players", "[]"))
    return [Player(**spec) for spec in player_specs]

def _save_players(response: Response, players: list[Player]) -> None:
    response.set_cookie("players", json.dumps([asdict(player) for player in players]))

from dataclasses import asdict

from flask import Blueprint, render_template, redirect, url_for, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange, ValidationError

import dmtoolkit.api.players as api

players_bp = Blueprint(
    "players_bp",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/players/static",
    url_prefix = "/players"
)

class CreateForm(FlaskForm):
    name = StringField("Name", [InputRequired()])
    ac = IntegerField("AC", [InputRequired(), NumberRange(min=0)])
    hp = IntegerField("Max HP", [InputRequired(), NumberRange(min=1, message="No!")])
    pp = IntegerField("Passive Perception", [InputRequired(), NumberRange(min=0)])
    submit = SubmitField("Create Player Character")

    def validate_name(self, field):
        print("Validating...")
        players = api.list_players()
        if any(field.data == p.name for p in players):
            print("Name already used")
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
    players = api.list_players()
    return render_template("list_players.jinja2", page=page, players=players)


@players_bp.route("/new", methods=["GET", "POST"])
def new_player_page():
    form = CreateForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        player = {
            "name": form.name.data,
            "ac": form.ac.data,
            "pp": form.pp.data,
            "hp": form.hp.data
        }
        print("NEW")
        resp = make_response(redirect(url_for("players_bp.list_players_page")))
        api.create_player(resp, player)
        return resp
    
    page = {
        "title": "DMTools - New Player"
    }
    return render_template("new_player.jinja2", page=page, form=form)


@players_bp.route("/edit/<player_name>", methods=["GET","POST"])
def update_player_page(player_name: str):
    form = UpdateForm()
    players = api.list_players()
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
        new_player = api.Player(**player_dict)
        if new_player.name != player.name and any(p.name == new_player.name for p in players):
            # TODO: Handle this more gracefully
            raise ValueError(f"Cannot rename player to '{new_player.name}' as this name is already in use")
        idx = players.index(player)
        players[idx] = new_player

        resp = make_response(redirect(url_for("players_bp.list_players_page")))
        api._save_players(resp, players)
        return resp
    
    page = {
        "title": f"DMTools - Edit {player_name}"
    }
    return render_template("edit_player.jinja2", page=page, player=player, form=form)

@players_bp.route("/delete/<player_name>", methods=["GET"])
def delete_player(player_name: str):
    resp = make_response(redirect(url_for("players_bp.list_players_page")))
    api.delete_player(resp, player_name)
    return resp

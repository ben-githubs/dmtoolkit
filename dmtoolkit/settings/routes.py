import json

from flask import Blueprint, flash, render_template, make_response

from dmtoolkit.settings.forms import SettingsForm
from dmtoolkit.settings.api import get_settings, set_settings

settings_bp = Blueprint(
    "settings_bp",
    __name__,
    template_folder = "templates",
    static_folder = "static",
    static_url_path = "/settings/static",
    url_prefix = "/settings"
)

@settings_bp.route("/edit", methods=["GET", "POST"])
def settings():
    page = {
        "title": "DMTools - Settings"
    }
    form = SettingsForm()
    settings = get_settings()

    if form.validate_on_submit():
        resp = make_response(render_template("settings.jinja2", page=page, form=form))
        resp = set_settings(form.data, resp)
        flash("Settings saved!", "success")
        return resp
    else:
        for field_name in form.data.keys():
            form[field_name].data = settings.get(field_name, False)
    
    return render_template("settings.jinja2", page=page, form=form)
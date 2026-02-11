import json
from typing import Any

from flask import Blueprint, flash, render_template, make_response
from wtforms import BooleanField

from dmtoolkit.modules import get_modules
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
    modules = get_modules()
    settings = get_settings()

    # Add widgets for each module dynamically
    # https://wtforms.readthedocs.io/en/2.3.x/specific_problems/#dynamic-form-composition
    class Form(SettingsForm):
        pass

    module_form_data: dict[str, dict[str, Any]] = {name: {"module": module} for name, module in modules.items()}
    
    for module_id, module in modules.items():
        field = BooleanField(module.description, default=False)
        setattr(Form, f"module_{module_id}", field)
        module_form_data[module_id]["field"] = field

    form = Form()

    if form.validate_on_submit():
        resp = make_response(render_template("settings.jinja2", page=page, form=form, module_form_data=module_form_data))
        resp = set_settings(form.data, resp)
        flash("Settings saved!", "success")
        return resp
    else:
        for field_name in form.data.keys():
            form[field_name].data = settings.get(field_name, False)
    
    return render_template("settings.jinja2", page=page, form=form, module_form_data=module_form_data)
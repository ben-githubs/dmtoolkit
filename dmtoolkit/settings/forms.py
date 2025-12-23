from flask_wtf import FlaskForm

from wtforms import SubmitField, BooleanField

class SettingsForm(FlaskForm):
    use_new_content = BooleanField("Use 5.5e Content?", default=False)
    
    module_kcg = BooleanField("Kibble's Crafting Guide", default=False)

    submit = SubmitField("Save Changes")
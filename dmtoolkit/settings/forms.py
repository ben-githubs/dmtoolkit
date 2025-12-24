from flask_wtf import FlaskForm

from wtforms import SubmitField, BooleanField, FormField, FieldList

class ModuleForm(FlaskForm):
    """A Reusable subform for each module toggle."""
    enabled = BooleanField(default=False)

class SettingsForm(FlaskForm):
    use_new_content = BooleanField("Use 5.5e Content?", default=False)

    submit = SubmitField("Save Changes")
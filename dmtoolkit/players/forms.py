from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired

from dmtoolkit.api.races import list_races

class CreateForm(FlaskForm):
    name = StringField("Name", [DataRequired()])
    ac = IntegerField("AC", [DataRequired()])
    hp = IntegerField("Max HP", [DataRequired()])
    pp = IntegerField("Passive Perception", [DataRequired()])
    race = SelectField("Race", choices=list_races())
    submit = SubmitField("Create Player Character")

def UpdateForm():
    form = CreateForm()
    form.name.validators = ()
    form.ac.validators = ()
    form.hp.validators = ()
    form.pp.validators = ()
    form.submit.label.text = "Update Player"
    return form
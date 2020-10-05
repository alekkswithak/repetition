from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class URLForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('submit')


class DeckSettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    card_number = IntegerField('Old cards per go', validators=[DataRequired()])
    new_card_number = IntegerField('New cards per go', validators=[DataRequired()])
    multiplier = IntegerField('Multiplier', validators=[DataRequired()])
    entry_interval = IntegerField('Entry interval', validators=[DataRequired()])
    submit = SubmitField('submit')

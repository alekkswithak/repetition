from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    PasswordField,
    BooleanField
)
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


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

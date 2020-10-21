from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    PasswordField,
    BooleanField,
    TextAreaField,
)
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    EqualTo
)
from app.models import User


class URLForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('submit')


class ClipForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text')
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


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CustomDeckForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign In')

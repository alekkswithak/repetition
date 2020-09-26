from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class URLForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('submit')
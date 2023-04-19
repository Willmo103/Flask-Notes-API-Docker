from app import User, Note
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    SelectField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class NoteForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content')
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    Email = StringField('Email', validators=[Email()], description="This is optional, provides a way to reset your password if you forget it., as well as allowing you to email notes to yourself.")
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

class NoteEditForm(FlaskForm):
    def self__init__(self, note_id):
        note = Note.query.get_or_404(note_id)
        self.title = StringField('Title', default=note.title)
        self.content = TextAreaField('Content', default=note.content)
        self.submit = SubmitField('Update Note')

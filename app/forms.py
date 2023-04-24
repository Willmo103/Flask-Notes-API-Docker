from app.models import User
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
from flask_wtf.file import FileField, FileRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class NoteForm(FlaskForm):
    title = StringField("Title")
    content = TextAreaField("Content")
    submit = SubmitField("Submit")
    private = BooleanField("Private", default=False)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")


class FileUploadForm(FlaskForm):
    file = FileField("Select a file", validators=[FileRequired()])
    details = StringField("Details", validators=[Length(max=200)])
    private = BooleanField("Private")
    submit = SubmitField("Upload")

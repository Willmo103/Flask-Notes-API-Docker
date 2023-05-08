from app.models import User
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    URLField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Optional,
    URL,
)
from flask_wtf.file import FileField


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


class AtLeastOneFileRequired:
    def __init__(self, message=None):
        if not message:
            message = "At least one file is required"
        self.message = message

    def __call__(self, form, field):
        other_field = form.file if field.name == "file_dz" else form.file_dz
        if not field.data and not other_field.data:
            raise ValidationError(self.message)


class FileUploadForm(FlaskForm):
    file = FileField("Select a file", validators=[Optional(), AtLeastOneFileRequired()])
    file_dz = FileField(
        "Select a file", validators=[Optional(), AtLeastOneFileRequired()]
    )
    details = StringField("Details", validators=[Length(max=200)])
    private = BooleanField("Private")
    submit = SubmitField("Upload")


class GroupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=200)])
    description = StringField("Description", validators=[Length(max=200)])
    submit = SubmitField("Add")


class BookmarkForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    href = URLField("URL", validators=[DataRequired(), URL()])
    details = TextAreaField("Details (optional)")
    group = StringField("Group", validators=[Length(max=200), DataRequired()])
    private = BooleanField("Private")
    submit = SubmitField("Add")


class EditFileForm(FlaskForm):
    details = StringField("Details", validators=[Length(max=200)])
    private = BooleanField("Private")
    submit = SubmitField("Save")


class DeleteFileForm(FlaskForm):
    reason = StringField(
        "Reason", validators=[Length(max=200)], default="No reason given"
    )
    submit = SubmitField("Delete")

from flask import (
    Response,
    flash,
    redirect,
    render_template,
    url_for,
    Blueprint,
    request,
    send_from_directory,
)
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from flask_wtf import FlaskForm
from app.models import User, Note, File, Upload, Download
from app.forms import (
    LoginForm,
    RegistrationForm,
    NoteForm,
    FileUploadForm,
    BookmarkForm,
    EditFileForm,
)
from werkzeug.utils import secure_filename as s_fn
import os
from datetime import datetime as dt

_upload_folder: str = os.environ.get("UPLOAD_FOLDER")
endpoint = Blueprint("routes", __name__)

@endpoint.context_processor
def inject_forms() -> dict:
    upload_form: FlaskForm = FileUploadForm()
    bookmark_form: FlaskForm = BookmarkForm()
    edit_file_form: FlaskForm = EditFileForm()
    return dict(upload_form=upload_form, bookmark_form=bookmark_form, edit_file_form=edit_file_form)

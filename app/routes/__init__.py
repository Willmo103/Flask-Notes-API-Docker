from flask import Blueprint
from flask_wtf import FlaskForm
from app.forms import (
    FileUploadForm,
    BookmarkForm,
    EditFileForm,
)

endpoint = Blueprint("routes", __name__)


@endpoint.context_processor
def inject_forms() -> dict:
    upload_form: FlaskForm = FileUploadForm()
    bookmark_form: FlaskForm = BookmarkForm()
    edit_file_form: FlaskForm = EditFileForm()
    return dict(
        upload_form=upload_form,
        bookmark_form=bookmark_form,
        edit_file_form=edit_file_form,
    )

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


from .files import (
    upload_file as upload_file,
    delete_file as delete_file,
    edit_file as edit_file,
    download_file as download_file,
)
from .groups import (
    create_group as create_group,
    edit_group as edit_group,
    delete_group as delete_group,
)
from .index import index_page as index_page
from .auth import login as login, logout as logout, register as register
from .bookmarks import (
    create_bookmark as create_bookmark,
    edit_bookmark as edit_bookmark,
    delete_bookmark as delete_bookmark,
)
from .notes import (
    add_note as add_note,
    edit_note as edit_note,
    delete_note as delete_note,
    get_user_notes as get_user_notes,
)

# from .users import * <-- TODO make routes for user edits in the future

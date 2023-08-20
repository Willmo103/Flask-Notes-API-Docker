from flask import Blueprint

endpoint = Blueprint("api", __name__)

from .files import (
    upload_file as upload_file,
    delete_file as delete_file,
    edit_file as edit_file,
    download_file as download_file,
)

from .auth import (
    login as login,
    logout as logout,
    register as register,
)

from .index import (
    get_notes as get_notes,
    get_files as get_files,
)

from .notes import (
    add_note as add_note,
    edit_note as edit_note,
    delete_note as delete_note,
    get_user_notes as get_user_notes,
)

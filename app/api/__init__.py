from flask import Blueprint

api = Blueprint("api", __name__)

from .api_files import (
    upload_file as upload_file,
    delete_file as delete_file,
    edit_file as edit_file,
    download_file as download_file,
)

from .api_index import (
    get_notes as get_notes,
    get_files as get_files,
)

from .api_notes import (
    add_note as add_note,
    edit_note as edit_note,
    delete_note as delete_note,
    get_user_notes as get_user_notes,
)

from flask import render_template, Response
from flask_login import current_user
from app.models import Note, File
from . import endpoint


@endpoint.route("/")
@endpoint.route("/index")
def index_page() -> str | Response:
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    notes = Note.index_page_notes(user_id)
    files = File.return_index_page_files(user_id)
    print("Files on index page", files)
    return render_template(
        "index.html",
        notes=notes,
        files=files,
        user=current_user,
        title="Info_Hub",
    )

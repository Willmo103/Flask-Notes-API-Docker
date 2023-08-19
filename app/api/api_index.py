from flask import Response, jsonify
from flask_login import current_user, login_required
from app.models import Note, File
from . import endpoint

# Endpoint to get notes
@endpoint.route("/api/notes", methods=["GET"])
# def get_notes():
def get_notes(request) -> Response:
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    limit = request.args.get('limit', default=10, type=int)
    skip = request.args.get('skip', default=0, type=int)
    notes = Note.index_page_notes(user_id, limit=limit, offset=skip)
    return jsonify(notes=[note.serialize() for note in notes])

# Endpoint to get files
@endpoint.route("/api/files", methods=["GET"])
def get_files():
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    limit = request.args.get('limit', default=10, type=int)
    skip = request.args.get('skip', default=0, type=int)
    files = File.return_index_page_files(user_id, limit=limit, offset=skip)
    return jsonify(files=[file.serialize() for file in files])

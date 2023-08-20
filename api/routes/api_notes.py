from flask import jsonify, request, Response
from flask_login import current_user, login_required
from api import db
from api.models import Note
from . import endpoint

__all__ = [
    "add_note",
    "edit_note",
    "delete_note",
    "get_user_notes",
    "search_notes",
]


@endpoint.route("/api/note/add", methods=["POST"])
def add_note():
    title = request.json["title"]
    content = request.json["content"]
    private = request.json["private"]

    note = Note(
        title=title,
        content=content,
        author=current_user if current_user.is_authenticated else None,
        private=private,
    )
    note.save()
    return jsonify(message="Your note has been saved.")


@endpoint.route("/api/note/<int:note_id>/edit", methods=["PUT"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if current_user.is_admin() or note.user_id == current_user.id:
        title = request.json["title"]
        content = request.json["content"]
        private = request.json["private"]

        note.title = title
        note.content = content
        note.private = private

        db.session.commit()
        return jsonify(message="Your note has been updated.")
    else:
        return jsonify(error="You do not have permission to edit this note."), 403


@endpoint.route("/api/note/<int:note_id>/delete", methods=["DELETE"])
@login_required
def delete_note(note_id) -> Response:
    note = Note.query.get_or_404(note_id)
    if note.delete(current_user.id, current_user.is_admin()):
        return jsonify(message="Your note has been deleted.")
    else:
        return jsonify(error="You do not have permission to delete this note."), 403


@endpoint.route("/api/user/notes", methods=["GET"])
@login_required
def get_user_notes() -> Response:
    notes = Note.get_user_notes(current_user.id)
    return jsonify(notes=[note.serialize() for note in notes])


@endpoint.route("/api/note/search", methods=["POST"])
def search_notes() -> Response:
    search_term = request.json["search_term"]
    try:
        id = current_user.id
    except AttributeError:
        id = None
    notes = Note.search(search_term, id)
    return jsonify(search_term=search_term, notes=[note.serialize() for note in notes])

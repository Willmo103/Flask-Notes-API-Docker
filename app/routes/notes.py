from flask import render_template, redirect, url_for, flash, Response, request
from flask_login import current_user, login_required
from app import db
from app.models import Note, User
from app.forms import NoteForm
from . import endpoint

__all__ = [
    "note",
    "edit_note",
    "delete_note",
    "get_user_notes",
    "search_notes",
]


@endpoint.route("/note/add", methods=["GET", "POST"])
def add_note() -> str | Response:
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            author=current_user if current_user.is_authenticated else None,
            private=form.private.data,
        )
        note.save()
        flash("Your note has been saved.")
        return redirect(url_for("routes.index_page"))
    return render_template("note.html", title="New Note", form=form, user=current_user)


@endpoint.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id) -> str | Response:
    note = Note.query.get_or_404(note_id)
    if current_user.is_admin() or note.user_id == current_user.id:
        form = NoteForm(title=note.title, content=note.content, private=note.private)
        if form.validate_on_submit():
            note.title = form.title.data
            note.content = form.content.data
            note.private = form.private.data
            db.session.commit()
            flash("Your note has been updated.")
            return redirect(url_for("routes.index_page"))
    else:
        flash("You do not have permission to edit this note.")
        return redirect(url_for("routes.index_page"))
    return render_template("note.html", title="Edit Note", form=form, user=current_user)


@endpoint.route("/note/<int:note_id>/delete", methods=["GET", "POST"])
@login_required
def delete_note(note_id) -> Response:
    note = Note.query.get_or_404(note_id)
    if note.delete(current_user.id, current_user.is_admin()):
        flash("Your note has been deleted.")
    else:
        flash("You do not have permission to delete this note.")
    return redirect(url_for("routes.index_page"))


@endpoint.route("/user/<int:user_id>/notes")
@login_required
def get_user_notes(user_id) -> Response:
    user = User.query.get_or_404(user_id)
    notes = user.get_notes()
    return render_template("index.html", notes=notes, user=user)


@endpoint.route("/note/search", methods=["GET", "POST"])
def search_notes() -> Response:
    if request.method == "POST":
        search_term = request.form["search_term"]
        try:
            id = current_user.id
        except AttributeError:
            id = None
        notes = Note.search(search_term, id)
        if len(notes) == 0 :
            notes = None
        return render_template(
            "note_search_results.html",
            search_term=search_term,
            notes=notes,
            title=f"Search Results for {search_term}",
        )
    return redirect(url_for("routes.index_page"))

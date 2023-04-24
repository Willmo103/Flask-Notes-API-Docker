from flask import flash, redirect, render_template, url_for, Blueprint, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Note, File
from app.forms import LoginForm, RegistrationForm, NoteForm, FileUploadForm
from werkzeug.utils import secure_filename
import os
from datetime import datetime as dt

upload_folder = os.environ.get("UPLOAD_FOLDER")
endpoint = Blueprint("routes", __name__)


@endpoint.context_processor
def inject_forms():
    form = FileUploadForm()
    return dict(form=form)


@endpoint.route("/")
@endpoint.route("/index")
def index():
    File.sync_files()
    notes = Note.return_index_page_notes(
        current_user.id if current_user.is_authenticated else None
    )
    files = File.return_index_page_files(
        current_user.id if current_user.is_authenticated else None
    )
    return render_template(
        "index.html",
        notes=notes,
        files=files,
        user=current_user,
        title="Info_Hub",
    )


@endpoint.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
        if current_user.is_authenticated:
            new_file = File(
                filename,
                user_id=current_user.id,
                date_posted=dt.utcnow(),
                private=form.private.data,
                details=form.details.data,
            )
        else:
            new_file = File(filename, date_posted=dt.utcnow())
        db.session.add(new_file)
        db.session.commit()
        flash("File uploaded successfully")
        return redirect(url_for("routes.index"))

    flash("File upload failed")
    return redirect(url_for("routes.index"))


@endpoint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("routes.login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("routes.index"))
    return render_template("login.html", title="Sign In", form=form)


@endpoint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("routes.index"))


@endpoint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        first_admin = User.query.filter_by(is_admin=True).first()
        if not first_admin:
            user.is_admin = True
        db.session.add(user)
        db.session.commit()
        flash(f"New user {form.username.data} has been created!")
        if User.query.count() == 1:
            flash("You are the first user, so you are an admin.")
        return redirect(url_for("routes.login"))
    return render_template("register.html", title="Register", form=form)


@endpoint.route("/note/add", methods=["GET", "POST"])
def note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            author=current_user if current_user.is_authenticated else None,
            private=form.private.data,
        )
        db.session.add(note)
        db.session.commit()
        flash("Your note has been saved.")
        return redirect(url_for("routes.index"))
    return render_template("note.html", title="New Note", form=form, user=current_user)


@endpoint.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if current_user.is_admin() or note.user_id == current_user.id:
        form = NoteForm(title=note.title, content=note.content, private=note.private)
        if form.validate_on_submit():
            note.title = form.title.data
            note.content = form.content.data
            note.private = form.private.data
            db.session.commit()
            flash("Your note has been updated.")
            return redirect(url_for("routes.index"))
    else:
        flash("You do not have permission to edit this note.")
        return redirect(url_for("routes.index"))
    return render_template("note.html", title="Edit Note", form=form, user=current_user)


@endpoint.route("/note/<int:note_id>/delete", methods=["GET", "POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.is_owned_by_user(current_user.id) or current_user.is_admin:
        db.session.delete(note)
        db.session.commit()
        flash("Your note has been deleted.")
    else:
        flash("You do not have permission to delete this note.")
    return redirect(url_for("routes.index"))


@endpoint.route("/user/<int:user_id>/notes")
@login_required
def get_user_notes(user_id):
    user = User.query.get_or_404(user_id)
    notes = user.get_notes()
    return render_template("index.html", notes=notes, user=user)


@endpoint.route("/search", methods=["GET", "POST"])
def search_notes():
    if request.method == "POST":
        search_term = request.form["search_term"]
        try:
            id = current_user.id
        except AttributeError:
            id = None
        notes = Note.search(search_term, id)
        return render_template(
            "search_results.html",
            notes=notes,
            title=f"Search Results for {search_term}",
        )
    return redirect(url_for("routes.index"))

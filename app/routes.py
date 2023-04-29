from flask import (
    Response,
    flash,
    redirect,
    render_template,
    url_for,
    Blueprint,
    request,
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
)
from werkzeug.utils import secure_filename
import os
from datetime import datetime as dt

_upload_folder: str = os.environ.get("UPLOAD_FOLDER")
endpoint = Blueprint("routes", __name__)


@endpoint.context_processor
def inject_forms() -> dict:
    upload_form: FlaskForm = FileUploadForm()
    bookmark_form: FlaskForm = BookmarkForm()
    return dict(upload_form=upload_form, bookmark_form=bookmark_form)


@endpoint.route("/")
@endpoint.route("/index")
def index() -> str | Response:
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    notes = Note.return_index_page_notes(user_id)
    files = File.return_index_page_files(user_id)

    return render_template(
        "index.html",
        notes=notes,
        files=files,
        user=current_user,
        title="Info_Hub",
    )


@endpoint.route("/upload_file", methods=["GET", "POST"])
def upload_file() -> str | Response:
    form = FileUploadForm()
    if form.validate_on_submit():
        time_stamp = dt.utcnow().strftime("%Y%m%d%H%M%S")
        file = form.file.data
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(_upload_folder, filename))
        if current_user.is_authenticated:
            new_file = File(
                filename,
                user_id=current_user.id,
                date_posted=time_stamp,
                private=form.private.data,
                details=form.details.data,
            )
            new_upload = Upload(
                user_id=current_user.id,
                file_id=filename,
                date_uploaded=time_stamp,
            )
        else:
            new_file = File(filename, date_posted=dt.utcnow())
            new_upload = Upload(file_id=filename, date_uploaded=time_stamp)

        new_upload.save()
        new_file.save()

        flash("File uploaded successfully")
        return redirect(url_for("routes.index"))

    flash("File upload failed")
    return redirect(url_for("routes.index"))


@endpoint.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
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
def logout() -> Response:
    logout_user()
    return redirect(url_for("routes.index"))


@endpoint.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
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
def note() -> str | Response:
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
            return redirect(url_for("routes.index"))
    else:
        flash("You do not have permission to edit this note.")
        return redirect(url_for("routes.index"))
    return render_template("note.html", title="Edit Note", form=form, user=current_user)


@endpoint.route("/note/<int:note_id>/delete", methods=["GET", "POST"])
@login_required
def delete_note(note_id) -> Response:
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
def get_user_notes(user_id) -> Response:
    user = User.query.get_or_404(user_id)
    notes = user.get_notes()
    return render_template("index.html", notes=notes, user=user)


@endpoint.route("/search", methods=["GET", "POST"])
def search_notes() -> Response:
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


@endpoint.route("/create_group", methods=["GET", "POST"])
def create_group() -> Response:
    # Implement group creation logic here
    pass


@endpoint.route("/edit_group/<int:group_id>", methods=["GET", "POST"])
def edit_group(group_id) -> Response:
    # Implement group editing logic here
    pass


@endpoint.route("/delete_group/<int:group_id>", methods=["POST"])
def delete_group(group_id) -> Response:
    # Implement group deletion logic here
    pass


@endpoint.route("/create_bookmark", methods=["GET", "POST"])
def create_bookmark() -> Response:
    # Implement bookmark creation logic here
    pass


@endpoint.route("/edit_bookmark/<int:bookmark_id>", methods=["GET", "POST"])
def edit_bookmark(bookmark_id) -> Response:
    # Implement bookmark editing logic here
    pass


@endpoint.route("/delete_bookmark/<int:bookmark_id>", methods=["POST"])
def delete_bookmark(bookmark_id) -> Response:
    # Implement bookmark deletion logic here
    pass

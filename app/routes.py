from flask import (
    Response,
    flash,
    redirect,
    render_template,
    url_for,
    Blueprint,
    request,
    send_from_directory,
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
    EditFileForm,
)
from werkzeug.utils import secure_filename as s_fn
import os
from datetime import datetime as dt


_upload_folder: str = os.environ.get("UPLOAD_FOLDER")
endpoint = Blueprint("routes", __name__)


@endpoint.context_processor
def inject_forms() -> dict:
    upload_form: FlaskForm = FileUploadForm()
    bookmark_form: FlaskForm = BookmarkForm()
    edit_file_form: FlaskForm = EditFileForm()
    return dict(upload_form=upload_form, bookmark_form=bookmark_form, edit_file_form=edit_file_form)


@endpoint.route("/")
@endpoint.route("/index")
def index() -> str | Response:
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


@endpoint.route("/upload_file", methods=["GET", "POST"])
def upload_file() -> str | Response:
    form = FileUploadForm()
    time_stamp = dt.utcnow().strftime("%Y%m%d%H%M%S")
    if form.file.data is None:
        uploaded_file = form.file_dz.data
    elif form.file_dz.data is None:
        uploaded_file = form.file.data

    filename = uploaded_file.filename
    content_type = uploaded_file.content_type
    content_length = uploaded_file.content_length
    secure_filename = s_fn(filename)

    print(filename)
    print(content_type)
    print(content_length)
    print(secure_filename)

    if current_user.is_authenticated:
        new_file = File(
            secure_filename,
            user_id=current_user.id,
            private=form.private.data,
            details=form.details.data,
        )
        new_file.save()

        file_id = File.query.filter_by(file_name=secure_filename).first().id
        new_upload = Upload(
            user_id=current_user.id,
            file_id=file_id,
        )

    else:
        new_file = File(secure_filename, date_posted=dt.utcnow())
        new_upload = Upload(file_id=secure_filename, date_uploaded=time_stamp)

    if new_file and new_upload:
        uploaded_file.save(os.path.join(_upload_folder, secure_filename))

    new_upload.save()

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
        user.save()
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
        note.save()
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
    if note.delete(current_user.id, current_user.is_admin()):
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


# TODO this needs to be a total search
@endpoint.route("/note/search", methods=["GET", "POST"])
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


@endpoint.route("/user/<int:user_id>/files")
@login_required
def get_user_files(user_id) -> Response:
    user = User.query.get_or_404(user_id)
    files = File.get_all_user_files(user_id)
    return render_template("index.html", files=files, user=user)


@endpoint.route("/group/add", methods=["GET", "POST"])
def create_group() -> Response:
    # Implement group creation logic here
    pass


@endpoint.route("/group/<int:group_id>/edit", methods=["GET", "POST"])
def edit_group(group_id) -> Response:
    # Implement group editing logic here
    pass


@endpoint.route("/group/<int:group_id>/delete", methods=["POST"])
def delete_group(group_id) -> Response:
    # Implement group deletion logic here
    pass


@endpoint.route("/bookmark/add", methods=["GET", "POST"])
def create_bookmark() -> Response:
    # Implement bookmark creation logic here
    pass


@endpoint.route("/bookmark/<int:bookmark_id>/edit", methods=["GET", "POST"])
def edit_bookmark(bookmark_id) -> Response:
    # Implement bookmark editing logic here
    pass


@endpoint.route("/bookmark/<int:bookmark_id>/delete", methods=["POST"])
def delete_bookmark(bookmark_id) -> Response:
    # Implement bookmark deletion logic here
    pass


@endpoint.route("/file/<int:file_id>/edit", methods=["GET", "POST"])
def edit_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    pass


@endpoint.route("/delete_file/<int:file_id>", methods=["DELETE"])
def delete_file(file_id) -> Response:
    pass


@endpoint.route("/file/<int:file_id>/download", methods=["GET"])
def download_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    if current_user.is_authenticated:
        if not file.is_private() or file.is_owned_by_user(current_user.id):
            Download.record_download(file_id, current_user.id)
            return send_from_directory(_upload_folder, file.file_name)
    elif not file.is_private() or file.is_anonymous():
        Download.record_download(file_id)
        return send_from_directory(_upload_folder, file.file_name)
    else:
        flash("You do not have permission to download this file.")
        return redirect(url_for("routes.login"))

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
    Response,
)
from flask_login import current_user, login_required
from app.models import File, Upload, Download, User, Deletion
from app.forms import FileUploadForm
from werkzeug.utils import secure_filename as s_fn
import os
from datetime import datetime as dt
from . import endpoint

_upload_folder: str = os.environ.get("UPLOAD_FOLDER")

@endpoint.route("/file/upload", methods=["GET", "POST"])
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
        return redirect(url_for("routes.index_page"))

    flash("File upload failed")
    return redirect(url_for("routes.index_page"))


@endpoint.route("/user/<int:user_id>/files")
@login_required
def get_user_files(user_id) -> Response:
    user = User.query.get_or_404(user_id)
    files = File.get_all_user_files(user_id)
    return render_template("index.html", files=files, user=user)


@endpoint.route("/file/<int:file_id>/edit", methods=["GET", "POST"])
def edit_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    pass


@endpoint.route("/delete_file/<int:file_id>", methods=["GET", "DELETE"])
@login_required
def delete_file(file_id) -> Response:
    if request.method == "GET":
        file = File.query.get_or_404(file_id)
        user = User.query.get_or_404(current_user.id)
        if user.is_admin() or file.is_owned_by_user(user.id):
            Deletion(file_id, user.id).save()
            file.delete()
            flash("Your file has been deleted.")


@endpoint.route("/file/<int:file_id>/download")
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

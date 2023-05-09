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
from app.forms import DeleteFileForm, FileUploadForm, EditFileForm
from werkzeug.utils import secure_filename as s_fn
import os
from datetime import datetime as dt
from . import endpoint

_upload_folder: str = os.environ.get("UPLOAD_FOLDER")


@endpoint.route("/file/upload", methods=["GET", "POST"])
def upload_file() -> str | Response:
    form = FileUploadForm()
    if form.file.data is None:
        uploaded_file = form.file_dz.data
    elif form.file_dz.data is None:
        uploaded_file = form.file.data
    else:
        flash("Failed to upload file")
        return redirect(url_for("routes.index_page"))

    secure_filename = s_fn(uploaded_file.filename)

    if current_user.is_authenticated:
        new_file_id = File.init_with_id(secure_filename)
        print("New file id", new_file_id)
        new_file: File = File.query.filter_by(file_name=secure_filename).first()
        if new_file:
            print("New file", new_file)
            new_file.user_id = current_user.id
            new_file.private = form.private.data
            new_file.details = form.details.data
            print("New file", new_file)
            new_file.save()
        else:
            raise Exception("Failed to create new file")

        new_upload = Upload(
            new_file.id,
            current_user.id,
        )
        print("New upload", new_upload)
        saved = new_upload.save()
    else:
        new_file = File.init_with_id(secure_filename)
        new_upload = Upload(file_id=new_file.id)
        saved = new_upload.save()

    if saved and new_file.id is not None:
        uploaded_file.save(os.path.join(_upload_folder, secure_filename))
        flash("File uploaded successfully")
        return redirect(url_for("routes.index_page"))

    flash("File upload failed")
    return redirect(url_for("routes.index_page"))


@endpoint.route("/user/<int:user_id>/files")
@login_required
def get_user_files(user_id) -> Response:
    user: User = User.query.get_or_404(user_id)
    files = File.get_all_user_files(user_id)
    return render_template("index.html", files=files, user=user)


@endpoint.route("/file/<int:file_id>/edit", methods=["GET", "POST"])
@login_required
def edit_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    form = EditFileForm()
    if request.method == "GET":
        return render_template(
            "file.html", title="Edit File", form=form, user=current_user, file=file
        )
    elif request.method == "POST":
        if current_user.is_admin() or file.is_owned_by_user(current_user.id):
            file.file_name = form.file_name.data
            file.private = form.private.data
            file.details = form.details.data
            file.save()
            flash("Your file has been updated.")
            return redirect(url_for("routes.index_page"))
        else:
            flash("You do not have permission to edit this file.")
            return redirect(url_for("routes.index_page"))


@endpoint.route("/file/<int:file_id>/delete", methods=["GET", "POST"])
@login_required
def delete_file(file_id) -> Response:
    file: File = File.query.get_or_404(file_id)
    form = DeleteFileForm()
    user = User.query.get_or_404(current_user.id)
    if user.is_admin():
        if request.method == "GET":
            return render_template(
                "delete_file.html",
                title="Delete File",
                form=form,
                file=file,
            )
        if form.validate_on_submit():
            file.delete()
            Deletion(file_id, current_user.id).save()
        flash("Your file has been deleted.")
        return redirect(url_for("routes.index_page"))
    else:
        flash("You do not have permission to delete this file.")
    return redirect(url_for("routes.index_page"))


from flask import Response, make_response


@endpoint.route("/file/<int:file_id>/download")
def download_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    if current_user.is_authenticated:
        if not file.is_private() or file.is_owned_by_user(current_user.id):
            Download.record_download(file_id, current_user.id)
            # setting the content headers so that the browser knows to download the file
            response = make_response(
                send_from_directory(_upload_folder, file.file_name, as_attachment=True)
            )
            response.headers[
                "Content-Disposition"
            ] = f"attachment; filename={file.file_name}"
            response.headers["Content-Type"] = "application/octet-stream"
            return response
    elif not file.is_private() or file.is_anonymous():
        Download.record_download(file_id)
        # setting the content headers so that the browser knows to download the file
        response = make_response(
            send_from_directory(_upload_folder, file.file_name, as_attachment=True)
        )
        response.headers[
            "Content-Disposition"
        ] = f"attachment; filename={file.file_name}"
        response.headers["Content-Type"] = "application/octet-stream"
        return response
    else:
        flash("You do not have permission to download this file.")
        return redirect(url_for("routes.login"))

from flask import request, jsonify, send_from_directory, Response
from flask_login import current_user, login_required
from app.models import File, Upload, Download, User, Deletion
from app.forms import DeleteFileForm, FileUploadForm, EditFileForm
from werkzeug.utils import secure_filename as s_fn
import os
from . import endpoint

_upload_folder: str = os.environ.get("UPLOAD_FOLDER")


@endpoint.route("/api/file/upload", methods=["POST"])
def upload_file():
    form = FileUploadForm()
    uploaded_file = request.files.get('file')

    if uploaded_file:
        secure_filename = s_fn(uploaded_file.filename)

        if current_user.is_authenticated:
            new_file: File = File.query.filter_by(file_name=secure_filename).first()
            if new_file:
                new_file.user_id = current_user.id
                new_file.private = request.json['private']
                new_file.details = request.json['details']
                new_file.save()
            else:
                return jsonify(error="Failed to create new file"), 400

            new_upload = Upload(new_file.id, current_user.id)
            saved = new_upload.save()
        else:
            new_file: File = File.query.filter_by(file_name=secure_filename).first()
            new_upload = Upload(file_id=new_file.id)
            saved = new_upload.save()

        if saved and new_file.id is not None:
            uploaded_file.save(os.path.join(_upload_folder, secure_filename))
            return jsonify(message="File uploaded successfully"), 201

        return jsonify(error="File upload failed"), 400

    return jsonify(error="No file uploaded"), 400


@endpoint.route("/api/user/files", methods=["GET"])
@login_required
def get_user_files() -> Response:
    files = File.get_all_user_files(current_user.id)
    return jsonify(files=[file.serialize() for file in files])


@endpoint.route("/api/file/<int:file_id>/edit", methods=["POST"])
@login_required
def edit_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    if current_user.is_admin() or file.is_owned_by_user(current_user.id):
        file.file_name = request.json['file_name']
        file.private = request.json['private']
        file.details = request.json['details']
        file.save()
        return jsonify(message="Your file has been updated."), 200

    return jsonify(error="You do not have permission to edit this file."), 403


@endpoint.route("/api/file/<int:file_id>/delete", methods=["POST"])
@login_required
def delete_file(file_id) -> Response:
    file: File = File.query.get_or_404(file_id)
    user = User.query.get_or_404(current_user.id)
    if user.is_admin():
        file.delete()
        Deletion(file_id, current_user.id).save()
        return jsonify(message="Your file has been deleted."), 200

    return jsonify(error="You do not have permission to delete this file."), 403


@endpoint.route("/api/file/<int:file_id>/download", methods=["GET"])
def download_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    if current_user.is_authenticated and (not file.is_private() or file.is_owned_by_user(current_user.id)) \
            or not file.is_private() or file.is_anonymous():
        Download.record_download(file_id, current_user.id if current_user.is_authenticated else None)
        return send_from_directory(_upload_folder, file.file_name, as_attachment=True)
    else:
        return jsonify(error="You do not have permission to download this file."), 403


@endpoint.route("/api/file/search", methods=["POST"])
def search_files() -> Response:
    search_term = request.json["search_term"]
    id = current_user.id if current_user.is_authenticated else None
    files = File.search(search_term, id)
    return jsonify(files=[file.serialize() for file in files] if files else [])


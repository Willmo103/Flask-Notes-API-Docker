from flask import jsonify, redirect, url_for, flash, request, Response
from flask_login import current_user, login_required
from app.models import File, Upload, Download, User, Deletion
from app.forms import DeleteFileForm, FileUploadForm, EditFileForm
from werkzeug.utils import secure_filename as s_fn
import os
from . import endpoint

_upload_folder: str = os.environ.get("UPLOAD_FOLDER")

# Endpoint for file upload
@endpoint.route("/api/file/upload", methods=["POST"])
def upload_file():
    file_data = request.json['file']
    private = request.json['private']
    details = request.json['details']
    secure_filename = s_fn(file_data['filename'])

    if current_user.is_authenticated:
        new_file: File = File.query.filter_by(file_name=secure_filename).first()
        if new_file:
            new_file.user_id = current_user.id
            new_file.private = private
            new_file.details = details
            new_file.save()
        else:
            return jsonify({"error": "Failed to create new file"}), 400

        new_upload = Upload(
            new_file.id,
            current_user.id,
        )
        saved = new_upload.save()
    else:
        new_file: File = File.query.filter_by(file_name=secure_filename).first()
        new_upload = Upload(file_id=new_file.id)
        saved = new_upload.save()

    if saved and new_file.id is not None:
        # Save file logic here
        return jsonify({"message": "File uploaded successfully"}), 201

    return jsonify({"error": "File upload failed"}), 400

# Endpoint to get user files
@endpoint.route("/api/user/files")
@login_required
def get_user_files() -> Response:
    files = File.get_all_user_files(current_user.id)
    return jsonify(files=[file.serialize() for file in files]), 200

# Endpoint to edit a file
@endpoint.route("/api/file/<int:file_id>/edit", methods=["POST"])
@login_required
def edit_file(file_id) -> Response:
    file = File.query.get_or_404(file_id)
    if current_user.is_admin() or file.is_owned_by_user(current_user.id):
        file.file_name = request.json['file_name']
        file.private = request.json['private']
        file.details = request.json['details']
        file.save()
        return jsonify({"message": "Your file has been updated."}), 200
    else:
        return jsonify({"error": "You do not have permission to edit this file."}), 403

# Endpoint to delete a file
@endpoint.route("/api/file/<int:file_id>/delete", methods=["POST"])
@login_required
def delete_file(file_id) -> Response:
    file: File = File.query.get_or_404(file_id)
    user = User.query.get_or_404(current_user.id)
    if user.is_admin() and request.json.get('confirmation', False):
        file.delete()
        Deletion(file_id, current_user.id).save()
        return jsonify({"message": "Your file has been deleted."}), 200
    else:
        return jsonify({"error": "You do not have permission to delete this file."}), 403

# Endpoint to download a file
# This remains unchanged, as download should provide a file response.
@endpoint.route("/api/file/<int:file_id>/download")
def download_file(file_id) -> Response:
    # Same logic
    ...

# Endpoint to search files
@endpoint.route("/api/file/search", methods=["POST"])
def search_files() -> Response:
    search_term = request.json['search_term']
    try:
        id = current_user.id
    except AttributeError:
        id = None
    files = File.search(search_term, id)
    return jsonify(files=[ file.serialize() for file in files if files else list([]) ]), 200

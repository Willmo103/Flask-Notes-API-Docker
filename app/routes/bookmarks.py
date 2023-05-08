from flask import render_template, redirect, url_for, flash, Response
from flask_login import current_user, login_required
from app.models import Bookmark
from app.forms import BookmarkForm
from . import endpoint


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

from flask import render_template, redirect, url_for, flash, Response
from flask_login import current_user, login_required
from app.models import Group
from app.forms import GroupForm
from . import endpoint

__all__ = [
    "create_group",
    "edit_group",
    "delete_group",
]

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

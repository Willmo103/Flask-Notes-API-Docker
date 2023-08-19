from flask import jsonify, request, Response
from flask_login import current_user, login_user, logout_user
from app.models import User
from . import endpoint

__all__ = [
    "login",
    "logout",
    "register",
]


@endpoint.route("/api/login", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return jsonify(message="Already authenticated"), 400

    username = request.json["username"]
    password = request.json["password"]
    remember_me = request.json["remember_me"]

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify(error="Invalid username or password"), 401

    login_user(user, remember=remember_me)
    return jsonify(message="Logged in successfully")


@endpoint.route("/api/logout", methods=["GET"])
def logout() -> Response:
    logout_user()
    return jsonify(message="Logged out successfully")


@endpoint.route("/api/register", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return jsonify(message="Already authenticated"), 400

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    user = User(username=username, email=email)
    user.set_password(password)
    first_admin = User.query.filter_by(is_admin=True).first()
    if not first_admin:
        user.is_admin = True

    user.save()
    if User.query.count() == 1:
        return jsonify(message=f"New user {username} has been created!", admin=True)

    return jsonify(message=f"New user {username} has been created!")

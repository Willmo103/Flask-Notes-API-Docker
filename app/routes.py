from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required, Blueprint
from app import db
from app.models import User, Note

endpoint = Blueprint("routes", __name__)

@endpoint.route("/")
@endpoint.route("/index")
def index():
    notes = Note.get_all_anonymous_notes()
    if current_user.is_authenticated:
        notes.extend(current_user.get_notes())
    return render_template("index.html", notes=notes)

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

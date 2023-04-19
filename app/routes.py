from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required, Blueprint
from app import db
from app.models import User, Note
from app.forms import LoginForm, RegistrationForm, NoteForm, NoteEditForm

endpoint = Blueprint("routes", __name__)

@endpoint.route("/")
@endpoint.route("/index")
def index():
    notes = Note.get_all_anonymous_notes()
    if current_user.is_authenticated:
        notes.extend(current_user.get_notes())
    return render_template("index.html", notes=notes, user=current_user or None)

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

@endpoint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("routes.index"))

@endpoint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.Email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"New user {form.username.data} has been created!")
        return redirect(url_for("routes.login"))
    return render_template("register.html", title="Register", form=form)

@endpoint.route("/note/add", methods=["GET", "POST"])
def note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
        )
        db.session.add(note)
        db.session.commit()
        flash("Your note has been saved.")
        return redirect(url_for("routes.index"))
    return render_template("note.html", title="New Note", form=form)


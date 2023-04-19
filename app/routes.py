from flask import flash, redirect, render_template, url_for, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
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
    return render_template("index.html", notes=notes, user=current_user)


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
        if User.query.count() > 0:
            user.is_admin = True
        db.session.add(user)
        db.session.commit()
        flash(f"New user {form.username.data} has been created!")
        if User.query.count() == 1:
            flash("You are the first user, so you are an admin.")
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


@endpoint.route("/note/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.is_owned_by_user(current_user.id) or current_user.is_admin():
        form = NoteEditForm(note_id)
        if form.validate_on_submit():
            note = Note.query.get_or_404(note_id)
            note.title = form.title.data
            note.content = form.content.data
            db.session.commit()
            flash("Your note has been updated.")
            return redirect(url_for("routes.index"))
    else:
        flash("You do not have permission to edit this note.")
        return redirect(url_for("routes.index"))
    return render_template("note.html", title="Edit Note", form=form)


@endpoint.route("/note/<int:note_id>/delete", methods=["GET", "POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.is_owned_by_user(current_user.id) or current_user.is_admin():
        db.session.delete(note)
        db.session.commit()
        flash("Your note has been deleted.")
    else:
        flash("You do not have permission to delete this note.")
    return redirect(url_for("routes.index"))


@endpoint.route("/user/<int:user_id>/notes")
@login_required
def get_user_notes(user_id):
    user = User.query.get_or_404(user_id)
    notes = user.get_notes()
    return render_template("index.html", notes=notes, user=user)

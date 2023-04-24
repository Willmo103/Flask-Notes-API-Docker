from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(60), nullable=False)
    notes = db.relationship("Note", backref="author", lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def get_notes(self):
        return Note.query.filter_by(user_id=self.id).all()

    def is_admin(self):
        return self.is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}')"


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True, default=None)
    content = db.Column(db.Text, nullable=True, default=None)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True, default=None
    )
    private = db.Column(db.Boolean, nullable=False, default=True)

    @staticmethod
    def get_all_anonymous_notes():
        notes = []
        notes_query = Note.query.all()
        for note in notes_query:
            if note.is_anonymous() or note.private is False:
                notes.append(note)
        return notes

    @staticmethod
    def search(search_term: str, user_id):

        # If user_id is None, only search anonymous notes
        if user_id is None:
            notes = Note.query.filter(
                and_(Note.content.contains(search_term), Note.user_id.is_(None))
            ).all()
        else:
            # Search for notes that are either owned by the user or are anonymous
            notes = Note.query.filter(
                Note.content.contains(search_term),
                or_(Note.user_id == user_id, Note.user_id.is_(None)),
            ).all()

        return notes

    def is_anonymous(self):
        return self.user_id is None

    def is_owned_by_user(self, user_id: int):
        return self.user_id == user_id

    def __repr__(self):
        return f"Note('{self.title}', '{self.date_posted}')"

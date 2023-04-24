from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped
from app import db, login_manager
from .note import Note
from .file import File
from .group import Group

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(20), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=True)
    password_hash: str = db.Column(db.String(120), nullable=False)
    notes: Mapped["Note"] = db.relationship("Note", backref="author", lazy=True)
    files: Mapped["File"] = db.relationship("File", backref="author", lazy=True)
    groups: Mapped["Group"] = db.relationship("Group", backref="author", lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def get_notes(self) -> List | None:
        return Note.query.filter_by(user_id=self.id).all()

    def is_admin(self) -> bool:
        return self.is_admin

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"User('{self.username}')"

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from app.models.note import Note
from app.models.file import File


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(20), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=True)
    password_hash: str = db.Column(db.String(120), nullable=False)
    notes = db.relationship("Note", backref="author", lazy=True)
    files = db.relationship("File", backref="author", lazy=True)
    groups = db.relationship("Group", backref="author", lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def is_admin(self) -> bool:
        return self.is_admin

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    def __repr__(self) -> str:
        return f"User('{self.username}')"

    def get_notes(self):
        return Note.query.filter_by(user_id=self.id).all()

    def get_files(self):
        return File.query.filter_by(user_id=self.id).all()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_user(user_id: int):
        user: User = User.query.filter_by(id=user_id).first()
        if user is None:
            raise Exception("User not found")
        return user

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
        }

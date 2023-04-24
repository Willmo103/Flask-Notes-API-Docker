import os
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager

_upload_folder = os.environ.get("UPLOADS_FOLDER")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(120), nullable=False)
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

    @staticmethod
    def return_index_page_notes(id):
        return Note.query.filter(
            or_(Note.user_id == id, Note.user_id.is_(None), Note.private.is_(False))
        ).all()


class File(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    date_posted: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_downloaded: datetime = db.Column(db.DateTime, nullable=True, default=None)
    owner_id: int = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True, default=None
    )
    file_name: str = db.Column(db.String(100), nullable=True, default=None)
    file_size: str = db.Column(db.String, nullable=True, default=None)
    file_type: str = db.Column(db.String(100), nullable=True, default=None)
    deleted: bool = db.Column(db.Boolean, nullable=False, default=False)
    date_deleted: datetime = db.Column(db.DateTime, nullable=True, default=None)
    private: bool = db.Column(db.Boolean, nullable=False, default=True)
    details: str = db.Column(db.String(200), nullable=True, default=None)

    def __init__(
        self, file_name: str, owner_id: int = None, date_posted: datetime = None, private: bool = False, details: str | None = None
    ) -> None:
        self.file_name = file_name
        self.owner_id = owner_id
        self.date_posted = date_posted
        self.private = private
        self.details = details

    @staticmethod
    def get_all_user_files(user_id: int) -> list:
        files = File.query.filter_by(user_id=user_id).all()
        return files

    @staticmethod
    def new_file(filename, owner_id) -> None:
        new_file: File = File(filename, owner_id, datetime.utcnow())
        db.session.add(new_file)
        db.session.commit()

    @staticmethod
    def delete_file(file_id) -> None:
        file: File = File.query.filter_by(id=file_id).first()
        # delete file from uploads folder
        os.remove(os.path.join(_upload_folder, file.file_name))
        file.deleted = True
        file.date_deleted = datetime.utcnow()
        db.session.update(file)
        db.session.commit()

    @staticmethod
    def return_index_page_files(id):
        File.read_info_from_uploads_dir()
        return File.query.filter(
            or_(File.owner_id == id, File.owner_id.is_(None), File.private.is_(False))
        ).all()

    @staticmethod
    def read_info_from_uploads_dir():
        for file in File.scan_folder():
            file_data = File.query.filter_by(file_name=file).first()
            if file_data is not None:
                if file_data.file_size is None:
                    file_data.file_size = f"{os.path.getsize(os.path.join(_upload_folder, file))/1000:.2f} MB"
                if file_data.file_type is None:
                    file_data.file_type = file.split(".")[-1]
                db.session.update(file_data)
                db.session.commit()

    @staticmethod
    def scan_folder():
        files = []
        for file in os.listdir(_upload_folder):
            if file != ".gitkeep":
                files.append(file)
            yield file

    @staticmethod
    def get_admin_files(current_user: User) -> list:
        if current_user.is_admin():
            return File.query.all()


class Download(db.Model):
    download_date: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user: int = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    file: int = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)

    def __init__(self, user, file):
        self.download_date = datetime.utcnow()
        self.user = user
        self.file = file

    @staticmethod
    def record_download(user, file):
        dl: Download = Download(user, file)
        db.session.add(dl)
        db.session.commit()

class Upload(db.Model):
    upload_date: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user: int = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    file: int = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)

    def __init__(self, user, file) -> None:
        self.upload_date = datetime.utcnow()
        self.user = user
        self.file = file

    @staticmethod
    def record_upload(user, file) -> None:
        ul: Upload = Upload(user, file)
        db.session.add(ul)
        db.session.commit()

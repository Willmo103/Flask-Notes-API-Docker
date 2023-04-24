import os
from typing import Generator, List
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager
from sqlalchemy.orm import Mapped

_upload_folder = os.environ.get("UPLOADS_FOLDER")


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

    def get_notes(self) -> List["Note"] | None:
        return Note.query.filter_by(user_id=self.id).all()

    def is_admin(self) -> bool:
        return self.is_admin

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"User('{self.username}')"


class Note(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(100), nullable=True, default=None)
    content: str = db.Column(db.Text, nullable=True, default=None)
    date_posted: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    user_id: Mapped["User"] = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True, default=None
    )
    private: bool = db.Column(db.Boolean, nullable=False, default=True)

    @staticmethod
    def get_all_anonymous_notes() -> List["Note"] | None:
        notes = []
        notes_query = Note.query.all()
        for note in notes_query:
            if note.is_anonymous() or note.private is False:
                notes.append(note)
        return notes

    @staticmethod
    def search(search_term: str, user_id) -> List["Note"] | None:
        if user_id is None:
            notes = Note.query.filter(
                and_(Note.content.contains(search_term), Note.user_id.is_(None))
            ).all()
        else:
            notes = Note.query.filter(
                Note.content.contains(search_term),
                or_(Note.user_id == user_id, Note.user_id.is_(None)),
            ).all()

        return notes

    def is_anonymous(self) -> bool:
        return self.user_id is None

    def is_private(self) -> bool:
        return self.private

    def is_owned_by_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def __repr__(self) -> str:
        return f"Note('{self.title}', '{self.date_posted}')"

    @staticmethod
    def return_index_page_notes(user: User | None) -> List["Note"] | None:
        if user is not None and user.is_authenticated:
            return Note.query.filter(
                or_(
                    Note.user_id == user.id,
                    Note.user_id.is_(None),
                    Note.private.is_(False),
                )
            ).all()
        return Note.query.filter(
            or_(Note.user_id == id, Note.user_id.is_(None), Note.private.is_(False))
        ).all()


class File(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    date_posted: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    last_downloaded: datetime = db.Column(db.DateTime, nullable=True, default=None)
    user_id: int = db.Column(
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
        self,
        file_name: str,
        user_id: int = None,
        date_posted: datetime = None,
        private: bool = False,
        details: str | None = None,
    ) -> None:
        self.file_name = file_name
        self.user_id = user_id
        self.date_posted = date_posted
        self.private = private
        self.details = details

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_user_files(user: User) -> list["File" | None]:
        if user.is_authenticated:
            return File.query.filter_by(user_id=user.id).all()

    @staticmethod
    def delete_file(file_id: int, user: User) -> None:
        file: File
        if not user.is_authenticated:
            return
        elif not user.is_admin:
            file: File = File.query.filter(
                and_(File.id == file_id, File.user_id == user.id)
            ).first()
        else:
            file: File = File.query.filter_by(id=file_id).first()
        # delete file from uploads folder
        os.remove(os.path.join(_upload_folder, file.file_name))
        file.deleted = True
        file.date_deleted = datetime.utcnow()
        db.session.update(file)
        db.session.commit()

    @staticmethod
    def return_index_page_files(user: User) -> list["File" | None]:
        File.read_info_from_uploads_dir()
        if user is not None and user.is_authenticated:
            return File.query.filter(
                or_(
                    File.user_id == user.id,
                    File.user_id.is_(None),
                    File.private.is_(False),
                )
            ).all()
        return File.query.filter(
            or_(File.user_id.is_(None), File.private.is_(False))
        ).all()

    @staticmethod
    def read_info_from_uploads_dir() -> None:
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
    def scan_folder() -> Generator[str, None, None]:
        files = []
        for file in os.listdir(_upload_folder):
            if file != ".gitkeep":
                files.append(file)
            yield file

    @staticmethod
    def get_admin_files(current_user: User) -> list["File" | None]:
        if current_user.is_admin():
            return File.query.all()

    def is_owned_by_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def is_anonymous(self) -> bool:
        return self.user_id is None

    def is_private(self) -> bool:
        return self.private

    def __repr__(self) -> str:
        return f"File('{self.file_name}', '{self.date_posted}')"


class Download(db.Model):
    download_date: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    user_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
        nullable=True,
        default=None,
    )
    file_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("file.id"), primary_key=True
    )

    def __init__(
        self,
        file_id: int,
        user_id: int | None = None,
        download_date: datetime = datetime.utcnow,
    ) -> None:
        self.download_date = download_date
        self.user = user_id
        self.file = file_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def record_download(file: id, user: id, time: datetime) -> None:
        dl: Download = Download(user, file, time)
        db.session.add(dl)
        db.session.commit()


class Upload(db.Model):
    upload_date: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    user_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
        nullable=True,
        default=None,
    )
    file_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("file.id"), primary_key=True
    )

    def __init__(
        self,
        file_id: int,
        user_id: int | None = None,
        upload_date: datetime = datetime.utcnow,
    ) -> None:
        self.upload_date = upload_date
        self.user_id = user_id
        self.file_id = file_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def record_upload(user_id: int, file_id: int) -> None:
        ul: Upload = Upload(user_id, file_id)
        db.session.add(ul)
        db.session.commit()


class Bookmark(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    date_posted: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    title: str = db.Column(db.String(100), nullable=False)
    href: str = db.Column(db.Text, nullable=False)
    details: str = db.Column(db.String(100), nullable=True, default=None)
    private: bool = db.Column(db.Boolean, nullable=False, default=False)
    user_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )
    group_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("group.id"), nullable=True
    )

    def __init__(
        self,
        title: str,
        href: str,
        private: bool,
        user_id: int,
        group_id: int,
        details: str = None,
    ) -> None:
        self.title = title
        self.href = href
        self.private = private
        self.user_id = user_id
        self.group_id = group_id
        self.details = details

    def __repr__(self):
        return f"Bookmark('{self.title}', '{self.href}', '{self.private}')"

    def return_group_bookmarks(self, group_id: int) -> list["Bookmark"]:
        return Bookmark.query.filter_by(group_id=group_id).all()

    def return_user_bookmarks(self, user_id: int) -> list["Bookmark"]:
        return Bookmark.query.filter_by(user_id=user_id).all()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()


class Group(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    private: bool = db.Column(db.Boolean, nullable=False, default=False)
    user_id: Mapped[int] = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )
    bookmarks: Mapped["Bookmark"] = db.relationship(
        "Bookmark", backref="group", lazy=True
    )

    def __init__(self, name: str, private: bool, user_id: int) -> None:
        self.name = name
        self.private = private
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"Group('{self.name}', '{self.private}')"

    def save(self, user: User) -> None:
        if not Group.group_exists(self.name, user):
            self.user_id = user.id
        db.session.add(self)
        db.session.commit()

    def group_exists(name: str, user: User | None) -> bool:
        if user is not None:
            if user.is_authenticated:
                return (
                    Group.query.filter_by(name=name, user_id=user.id).first()
                    is not None
                )
        return Group.query.filter_by(name=name).first() is not None

    def is_private(self) -> bool:
        return self.private

    def add_bookmark(self, bookmark: Bookmark) -> None:
        self.bookmarks.append(bookmark)
        db.session.commit()

    @staticmethod
    def return_index_page_groups_and_bookmarks(user: User) -> list["Group" | None]:
        if user.is_authenticated:
            return Group.query.filter_by(
                or_(
                    user_id=user.id,
                )
            ).all()

    @staticmethod
    def new_group(name: str, private: bool = False) -> None:
        new_group = Group(name=name, private=private)

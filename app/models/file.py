from app import db
from typing import List, Generator
from datetime import datetime
from sqlalchemy import or_, and_
import os

_upload_folder = os.environ.get("UPLOAD_FOLDER")


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
        date_posted: datetime = datetime.utcnow(),
        private: bool = False,
        details: str | None = None,
    ) -> None:
        self.file_name = file_name
        self.user_id = user_id
        self.date_posted = date_posted
        self.private = private
        self.details = details

    def __repr__(self) -> str:
        return f"File('{self.file_name}', '{self.date_posted}')"

    def is_owned_by_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def is_anonymous(self) -> bool:
        return self.user_id is None

    def is_private(self) -> bool:
        return self.private

    def save(self) -> int:
        db.session.add(self)
        db.session.flush()  # Replaces db.session.commit().returning(File.id)
        id = self.id
        db.session.commit()  # Commit the transaction
        return id

    def delete(self, user_id: int, admin: bool = False) -> bool:
        if self.is_owned_by_user(user_id) or admin:
            db.session.delete(self)
            db.session.commit()
            return True
        return False

    def is_editable(self, user_id: int) -> bool:
        return self.is_owned_by_user(user_id)

    @staticmethod
    def get_all_user_files(user_id) -> List | None:
        return File.query.filter_by(user_id=user_id).all()

    @staticmethod
    def delete_file(file_id: int, user) -> None:
        file: File = File.query.filter_by(id=file_id).first()
        if file:
            file: File = File.query.filter(
                and_(File.id == file_id, File.user_id == user.id)
            ).first()
        else:
            file: File = File.query.filter_by(id=file_id).first()
        os.remove(os.path.join(_upload_folder, file.file_name))
        file.deleted = True
        file.date_deleted = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def return_index_page_files(user_id: int) -> List | None:
        File.read_info_from_uploads_dir()
        if user_id is not None:
            return File.query.filter(
                and_(
                    or_(
                        File.user_id == user_id,
                        File.user_id.is_(None),
                        File.private.is_(False),
                    ),
                    File.deleted.is_(False),
                )
            ).all()
        return File.query.filter(
            and_(
                or_(File.user_id.is_(None), File.private.is_(False)),
                File.deleted.is_(False),
            )
        ).all()

    @staticmethod
    def read_info_from_uploads_dir() -> None:
        for file in File.scan_folder():
            file_data = File.query.filter_by(file_name=file).first()
            if file_data is not None:
                if file_data.file_size is None:
                    file_data.file_size = f"{os.path.getsize(os.path.join(_upload_folder, file))/1000:.2f} MB"
                    print("File size: ", file_data.file_size)
                if file_data.file_type is None:
                    file_data.file_type = file.split(".")[-1]
                    print("File type: ", file_data.file_type)
                db.session.commit()

    @staticmethod
    def scan_folder() -> Generator[str, None, None]:
        for file in os.listdir(_upload_folder):
            print("File: ", file)
            yield file

    @staticmethod
    def get_admin_files(current_user) -> List | None:
        if current_user.is_admin():
            return File.query.all()

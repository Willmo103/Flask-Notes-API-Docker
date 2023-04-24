from datetime import datetime
from sqlalchemy.orm import Mapped
from app import db

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
    file_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)

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

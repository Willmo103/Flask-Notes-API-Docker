from datetime import datetime
from sqlalchemy.orm import Mapped
from app import db

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
    file_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)

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


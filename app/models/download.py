from datetime import datetime
from app import db


class Download(db.Model):
    download_date: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
        nullable=True,
        default=None,
    )
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)

    def __init__(
        self,
        file_id: int,
        user_id: int | None = None,
        download_date: datetime = datetime.utcnow(),
    ) -> None:
        self.user_id = user_id
        self.file_id = file_id
        self.download_date = download_date

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def record_download(cls, file_id, user_id):
        download = cls(
            file_id=file_id,
            user_id=user_id,  # Set user_id field here
            download_date=datetime.utcnow(),
        )
        db.session.add(download)
        db.session.commit()

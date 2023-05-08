from app import db
from datetime import datetime
from app.models.user import User


class Deletion(db.Model):
    deletion_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted_by = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    file_deleted = db.Column(db.Integer, db.ForeignKey("file.id"), primary_key=True)
    reason_deleted = db.Column(db.String(1000), nullable=True, default=None)

    def __init__(user_id: int, file_id: int, reason: str = None) -> None:
        User.get_user(user_id)
        if user.is_admin == False:
            raise Exception("User is not an admin")
        self.deletion_date = datetime.utcnow()
        self.deleted_by = user_id
        self.file_deleted = file_id
        self.reason_deleted = reason

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

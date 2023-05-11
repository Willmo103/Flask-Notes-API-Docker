from typing import List
from datetime import datetime
from sqlalchemy import or_, and_
from app import db


class Note(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(100), nullable=True, default=None)
    content: str = db.Column(db.Text, nullable=True, default=None)
    date_posted: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="NO ACTION"),
        nullable=True,
        default=None,
    )
    private: bool = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"Note('{self.title}', '{self.date_posted}')"

    def is_anonymous(self) -> bool:
        return self.user_id is None

    def is_private(self) -> bool:
        return self.private

    def is_owned_by_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self, user_id: int, admin: bool = False) -> bool:
        if self.is_owned_by_user(user_id) or admin:
            db.session.delete(self)
            db.session.commit()
            return True
        return False

    def is_viewable_by_user(self, user_id: int | None) -> bool:
        if user_id is None:
            return not self.private or self.is_anonymous()
        return self.is_owned_by_user(user_id) or not self.private

    @staticmethod
    def get_all_anonymous_notes() -> List | None:
        return Note.query.filter_by(user_id=None).all()

    @staticmethod
    def search(search_term: str, user_id) -> List:
        if search_term != "":
            return [
                note
                for note in Note.query.filter(
                    or_(
                        Note.content.contains(search_term), Note.title.contains(search_term)
                    )
                ).all()
                if note.is_viewable_by_user(user_id)
            ]
        return []

    @staticmethod
    def index_page_notes(user_id: int | None) -> List | None:
        return [note for note in Note.query.all() if note.is_viewable_by_user(user_id)]

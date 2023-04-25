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
        db.Integer, db.ForeignKey("user.id"), nullable=True, default=None
    )
    private: bool = db.Column(db.Boolean, nullable=False, default=True)

    def is_anonymous(self) -> bool:
        return self.user_id is None

    def is_private(self) -> bool:
        return self.private

    def is_owned_by_user(self, user_id: int) -> bool:
        return self.user_id == user_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()


    def __repr__(self) -> str:
        return f"Note('{self.title}', '{self.date_posted}')"

    @staticmethod
    def get_all_anonymous_notes() -> List | None:
        notes = []
        notes_query = Note.query.all()
        for note in notes_query:
            if note.is_anonymous() or note.private is False:
                notes.append(note)
        return notes

    @staticmethod
    def search(search_term: str, user_id) -> List | None:
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


    @staticmethod
    def return_index_page_notes(user_id: int | None) -> List | None:
        if user_id is not None:
            return Note.query.filter(
                or_(
                    Note.user_id == user_id,
                    Note.user_id.is_(None),
                    Note.private.is_(False),
                )
            ).all()
        return Note.query.filter(
            or_(Note.user_id == id, Note.user_id.is_(None), Note.private.is_(False))
        ).all()

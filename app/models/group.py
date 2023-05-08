from typing import List
from sqlalchemy import or_
from app import db


class Group(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    private: bool = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    bookmarks = db.relationship("Bookmark", backref="group", lazy=True)

    def __init__(self, name: str, private: bool, user_id: int) -> None:
        self.name = name
        self.private = private
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"Group('{self.name}', '{self.private}')"

    def save(self, user) -> None:
        if not Group.group_exists(self.name, user):
            self.user_id = user.id
        db.session.add(self)
        db.session.commit()

    def group_exists(name: str, user) -> bool:
        if user is not None:
            if user.is_authenticated:
                return (
                    Group.query.filter_by(name=name, user_id=user.id).first()
                    is not None
                )
        return Group.query.filter_by(name=name).first() is not None

    def is_private(self) -> bool:
        return self.private

    def add_bookmark(self, bookmark) -> None:
        self.bookmarks.append(bookmark)
        db.session.commit()

    @staticmethod
    def return_index_page_groups_and_bookmarks(user) -> List | None:
        if user.is_authenticated:
            return Group.query.filter_by(
                or_(
                    user_id=user.id,
                )
            ).all()

    @staticmethod
    def new_group(name: str, private: bool = False) -> None:
        new_group = Group(name=name, private=private)

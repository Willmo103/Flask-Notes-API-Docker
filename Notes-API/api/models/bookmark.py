from api import db
from datetime import datetime


class Bookmark(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    date_posted: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    title: str = db.Column(db.String(100), nullable=False)
    href: str = db.Column(db.Text, nullable=False)
    details: str = db.Column(db.String(100), nullable=True, default=None)
    private: bool = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    group_id = db.Column(
        db.Integer, db.ForeignKey("group.id", ondelete="No ACTION"), nullable=True
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

    def return_group_bookmarks(self, group_id: int):
        return Bookmark.query.filter_by(group_id=group_id).all()

    def return_user_bookmarks(self, user_id: int):
        return Bookmark.query.filter_by(user_id=user_id).all()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

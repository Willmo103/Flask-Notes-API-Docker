import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super_secret_key"

    if (
        os.environ.get("PG_USER")
        and os.environ.get("PG_PASSWORD")
        and os.environ.get("PG_HOST")
        and os.environ.get("PG_PORT")
        and os.environ.get("PG_DBNAME")
    ):
        SQLALCHEMY_DATABASE_URI = (
            "postgresql://"
            + os.environ.get("PG_USER")
            + ":"
            + os.environ.get("PG_PASSWORD")
            + "@"
            + os.environ.get("PG_HOST")
            + ":"
            + os.environ.get("PG_PORT")
            + "/"
            + os.environ.get("PG_DBNAME")
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///myNotes.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

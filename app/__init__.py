from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import markdown
import os

basedir = os.path.abspath(os.path.dirname(__file__))

db: SQLAlchemy = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "routes.login"

# Add Jinja2 filter for Markdown conversion
def markdown_filter(content):
    return markdown.markdown(content)


def create_app():
    print(__name__, "is the name of the app")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or "5S3eCcRe3et_kKke3ey"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///notes.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True


    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes
        from . import models

        app.register_blueprint(routes.endpoint)

        # Register the markdown filter with the app
        app.jinja_env.filters["markdown"] = markdown_filter

        db.create_all()

        return app

app = create_app()

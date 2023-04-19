from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import markdown

db: SQLAlchemy = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "routes.login"

# Add Jinja2 filter for Markdown conversion
def markdown_filter(content):
    return markdown.markdown(content)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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

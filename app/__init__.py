from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .utils import init_db_config
import dotenv, hashlib, markdown, os


app_dir = os.path.abspath(os.path.dirname(__file__))
root = os.path.abspath(os.path.join(app_dir, os.pardir))
env_path = os.path.join(root, '.env')
check_for_dotenv = os.path.exists(env_path)
print(f"checking if .env file exists: {check_for_dotenv}")
if check_for_dotenv:
    # if the .env file exists, load it into the environment
    dotenv.load_dotenv(env_path)
    init_db_config(env_path)
    try:
        os.environ.get('SECRET_KEY')
        print('Found SECRET_KEY in .env file')
    except KeyError:
        print('SECRET_KEY not found in .env file')
        print('Setting default SECRET_KEY')
        os.environ['SECRET_KEY'] = hashlib.sha256(os.urandom(64)).hexdigest()
        print('generated a new SECRET_KEY')
        print('writing default SECRET_KEY to .env file')
        with open(env_path, 'a') as f:
            f.write(f'\nSECRET_KEY={os.environ["SECRET_KEY"]}')
    try:
        os.environ.get('UPLOAD_FOLDER')
        print('Found UPLOAD_FOLDER in .env file')
        # update the uploads folder in the .env file to the absolute path if not already an absolute path
        print('checking if UPLOAD_FOLDER is an absolute path')
        if not os.path.isabs(os.environ['UPLOAD_FOLDER']):
            print('UPLOAD_FOLDER is not an absolute path')
            print('updating UPLOAD_FOLDER to absolute path')
            os.environ['UPLOAD_FOLDER'] = os.path.join(root, os.environ['UPLOAD_FOLDER'])
            print('writing absolute path to .env file')
            # first remove the old UPLOAD_FOLDER from the .env file
            with open(env_path, 'r') as f:
                lines = f.readlines()
            with open(env_path, 'w') as f:
                for line in lines:
                    if not line.startswith('UPLOAD_FOLDER'):
                        f.write(line)
            with open(env_path, 'a') as f:
                f.write(f'\nUPLOAD_FOLDER={os.environ["UPLOAD_FOLDER"]}')
    except KeyError:
        print('UPLOAD_FOLDER not found in .env file')
        print('Setting default UPLOAD_FOLDER')
        os.environ['UPLOAD_FOLDER'] = os.path.join(root, 'uploads')
        # update the uploads folder in the .env file to the absolute path
        with open(env_path, 'a') as f:
            f.write(f'\nUPLOAD_FOLDER={os.environ["UPLOAD_FOLDER"]}')
        print('writing default UPLOAD_FOLDER to .env file')
    # additional configuration can be added here
    # for example, to add support for other databases, add the database configuration to the .env file
else:
    # set defaults for all environment variables and write them to the .env file
    print('No .env file found')
    print('Setting default database configuration')


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "5S3eCcRe3et_kKke3ey"


db: SQLAlchemy = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "routes.login"




# Add Jinja2 filter for Markdown conversion
def markdown_filter(content):
    return markdown.markdown(content)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.environ.get("DATABASE_URL") or "sqlite:///notes.db" # postgresql://user:password@localhost:5432/dbname
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False

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

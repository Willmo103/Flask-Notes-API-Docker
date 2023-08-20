from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .utils import init_db_config, init_uploads_folder, init_secret_key
import dotenv, markdown, os

# set the project root directory as an environment variable to be used in other modules
os.environ["PROJECT_ROOT"] = os.path.abspath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
)
os.environ["ENV_PATH"] = os.path.join(os.environ.get("PROJECT_ROOT"), ".env")
check_for_dotenv = os.path.exists(os.environ.get("ENV_PATH"))
print(f"checking if .env file exists: {check_for_dotenv}")

# load or create .env file
if check_for_dotenv:
    # if the .env file exists, load it into the environment
    dotenv.load_dotenv(dotenv_path=os.environ.get("ENV_PATH"))
else:
    # create a .env file if it does not exist
    with open(os.environ.get("ENV_PATH"), "w") as f:
        f.write("")

# run the configuration functions
init_db_config()
init_uploads_folder()
init_secret_key()


# initialize the api configuration with the utils module and Config class
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    UPLOADS_FOLDER = os.environ.get("UPLOADS_FOLDER")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") or False
    )
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO") or False


# create an instance of the Config class
conf = Config()

# initialize the database
db: SQLAlchemy = SQLAlchemy()

# initialize the login manager
login_manager = LoginManager()

# set the login view for the login manager
login_manager.login_view = "api.login"

# create the api factory function and register the blueprints and database
def create_api():
    # create the flask api instance
    api = Flask(__name__)

    # load the api configuration
    api.config.from_object(Config)

    # initialize the database
    db.init_api(api)

    # initialize the login manager
    login_manager.init_api(api)

    # using the api context, register the blueprints and models
    with api.api_context():

        # import the routes and models modules
        from . import models
        from . import routes

        # register the blueprints
        api.register_blueprint(routes.endpoint)

        # create the database tables if they do not exist
        db.create_all()

        # return the api instance
        return api


# create the api instance
api = create_api()

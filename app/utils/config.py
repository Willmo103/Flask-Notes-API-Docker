import os, hashlib


def init_db_config():
    env_file = os.environ.get("ENV_PATH")
    try:
        # First check for postgres database configuration, it will be used if it exists
        # this can be easily extended to support other databases
        os.environ.get("DATABASE_URL_POSTGRES")
        os.environ["DB_TYPE"] = "postgres"
        print("Found postgres database configuration")
        print(
            f'Connecting to postgres database {os.environ.get("DATABASE_URL_POSTGRES").split("@")[1].split("/")[1]}'
        )
    except KeyError:
        print("DATABASE_URL_POSTGRES not found in .env file")
        print("Looking for sqlite database configuration")
        os.environ["DB_TYPE"] = "postgres"
        try:
            os.environ.get("SQLALCHEMY_DATABASE_URI_SQLITE")
            print("Found sqlite database configuration")
            print(
                f'Connecting to sqlite database {os.environ.get("SQLALCHEMY_DATABASE_URI_SQLITE").split("///")[1].split(".")[0]}'
            )
        except KeyError:
            # if no database configuration is found, set a default sqlite database configuration
            print("DATABASE_URL_SQLITE not found in .env file")
            print("Setting default sqlite database configuration")
            os.environ["SQLALCHEMY_DATABASE_URI_SQLITE"] = "sqlite:///notes.db"
            print("connecting to default sqlite database notes.db")
            print("writing default sqlite database configuration to .env file")
            with open(env_file, "a") as f:
                f.write(f"DATABASE_URL_SQLITE=sqlite:///notes.db")
    # additional configuration can be added here
    if os.environ["DB_TYPE"] == "postgres":
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_POSTGRES")
    elif os.environ["DB_TYPE"] == "sqlite":
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_SQLITE")
    else:
        raise Exception("Database type not supported")
    os.environ["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    # write SQLALCHEMY_DATABASE_URI to .env file if not already present
    with open(env_file, "r") as f:
        lines = f.readlines()
    if not any('SQLALCHEMY_DATABASE_URI' in line for line in lines):
        with open(env_file, "w") as f:
            for line in lines:
                if "SQLALCHEMY_DATABASE_URI" not in line:
                    f.write(line)

        with open(env_file, "a") as f:
            f.write(f"""\nSQLALCHEMY_DATABASE_URI='{SQLALCHEMY_DATABASE_URI}'""")

    return


def init_uploads_folder():
    env_file = os.environ.get("ENV_PATH")
    root = os.environ.get("PROJECT_ROOT")
    try:
        UPLOADS_FOLDER = os.environ.get("UPLOAD_FOLDER")
        print("Found UPLOAD_FOLDER in .env file")
        # update the uploads folder in the .env file to the absolute path if not already an absolute path
        print("checking if UPLOAD_FOLDER is an absolute path")
        if not os.path.isabs(os.environ["UPLOAD_FOLDER"]):
            print("UPLOAD_FOLDER is not an absolute path")
            print("updating UPLOAD_FOLDER to absolute path")
            UPLOADS_FOLDER = os.path.join(root, os.environ["UPLOAD_FOLDER"])
            os.environ["UPLOAD_FOLDER"] = UPLOADS_FOLDER
            print("writing absolute path to .env file")
            # first remove the old UPLOAD_FOLDER from the .env file
            with open(env_file, "r") as f:
                lines = f.readlines()
            with open(env_file, "w") as f:
                for line in lines:
                    if not line.startswith("UPLOAD_FOLDER"):
                        f.write(line)
            with open(env_file, "a") as f:
                f.write(f"""\nUPLOAD_FOLDER='{os.environ["UPLOAD_FOLDER"]}\'""")
        else:
            print("UPLOAD_FOLDER is already an absolute path")
    except KeyError:
        print("UPLOAD_FOLDER not found in .env file")
        print("Setting default UPLOAD_FOLDER")
        UPLOADS_FOLDER = os.path.join(root, "uploads")
        os.environ["UPLOAD_FOLDER"] = UPLOADS_FOLDER
        # update the uploads folder in the .env file to the absolute path
        with open(env_file, "a") as f:
            f.write(f"""\nUPLOAD_FOLDER='{os.environ["UPLOAD_FOLDER"]}\'""")
        print("writing default UPLOAD_FOLDER to .env file")
    # additional configuration can be added here
    # for example, to add support for other databases, add the database configuration to the .env file
    if not os.path.exists(os.environ["UPLOAD_FOLDER"]):
        print("creating uploads folder")
        os.mkdir(os.environ["UPLOAD_FOLDER"])
    return


def init_secret_key():
    env_file = os.environ.get("ENV_PATH")
    try:
        os.environ.get("SECRET_KEY")
        print("Found SECRET_KEY in .env file")
    except KeyError:
        print("SECRET_KEY not found in .env file")
        print("Setting default SECRET_KEY")
        SECRET_KEY = hashlib.sha256(os.urandom(64)).hexdigest()
        os.environ["SECRET_KEY"] = SECRET_KEY
        print("generated a new SECRET_KEY")
        print("writing default SECRET_KEY to .env file")
        with open(env_file, "a") as f:
            f.write(f'\nSECRET_KEY={os.environ["SECRET_KEY"]}')
    return

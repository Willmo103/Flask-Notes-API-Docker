import os

def init_db_config(env):
    try:
        # First check for postgres database configuration, it will be used if it exists
        # this can be easily extended to support other databases
        os.environ.get('DATABASE_URL_POSTGRES')
        os.environ['DB_TYPE'] = 'postgres'
        print('Found postgres database configuration')
        print(f'Connecting to postgres database {os.environ.get("DATABASE_URL_POSTGRES").split("@")[1].split("/")[1]}')
    except KeyError:
        print('DATABASE_URL_POSTGRES not found in .env file')
        print('Looking for sqlite database configuration')
        os.environ['DB_TYPE'] = 'postgres'
        try:
            os.environ.get('SQLALCHEMY_DATABASE_URI_SQLITE')
            print('Found sqlite database configuration')
            print(f'Connecting to sqlite database {os.environ.get("SQLALCHEMY_DATABASE_URI_SQLITE").split("///")[1].split(".")[0]}')
        except KeyError:
            # if no database configuration is found, set a default sqlite database configuration
            print('DATABASE_URL_SQLITE not found in .env file')
            print('Setting default sqlite database configuration')
            os.environ['SQLALCHEMY_DATABASE_URI_SQLITE'] = 'sqlite:///notes.db'
            print('connecting to default sqlite database notes.db')
            print('writing default sqlite database configuration to .env file')
            with open(env, 'a') as f:
                f.write(f'\nDATABASE_URL_SQLITE=sqlite:///notes.db')
    # additional configuration can be added here
    if os.environ['DB_TYPE'] == 'postgres':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_POSTGRES')
    elif os.environ['DB_TYPE'] == 'sqlite':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_SQLITE')
    else:
        raise Exception('Database type not supported')
    os.environ['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    # write SQLALCHEMY_DATABASE_URI to .env file if not already present
    with open(env, 'r') as f:
        lines = f.readlines()
    if not any('SQLALCHEMY_DATABASE_URI' in line for line in lines):
        print('writing SQLALCHEMY_DATABASE_URI to .env file')
    with open(env, 'a') as f:
        f.write(f'\nSQLALCHEMY_DATABASE_URI={SQLALCHEMY_DATABASE_URI}')
    return

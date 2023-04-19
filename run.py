from app import create_app
from flask import Flask

if __name__ == '__main__':
    app: Flask = create_app()
    # app.run(debug=True) # debug=True is only for development
    app.run(host='Notes.local', port=5000, debug=True)

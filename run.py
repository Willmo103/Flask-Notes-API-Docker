from app import create_app
from flask import Flask

if __name__ == "__main__":
    app: Flask = create_app()
    # app.run(debug=True) # debug=True is only for development
    app.run(host="127.0.0.1", port=5000, debug=True)

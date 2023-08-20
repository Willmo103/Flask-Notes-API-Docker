from api import api

if __name__ == "__main__":
    api.run(
        host="127.0.0.1", port=5000, debug=True
    )  # debug=True is only for development
    # api.run()

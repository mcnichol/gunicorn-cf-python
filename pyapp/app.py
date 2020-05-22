from flask import Flask
import os
from pyapp.src.tree_ensemble_scoring import score

app = Flask(__name__)
PORT = int(os.getenv("PORT", 8080))


@app.route("/<name>")
def index(name):
    return "Hello "+name.upper() + str(score())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)

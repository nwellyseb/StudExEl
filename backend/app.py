from flask import Flask, render_template

from config import Config
from extensions import db
import models

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
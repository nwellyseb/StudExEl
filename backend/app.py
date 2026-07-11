from flask import Flask, render_template
from flask_migrate import Migrate

from config import Config
from extensions import db

from routes.auth import auth
from routes.marketplace import marketplace
from routes.listings import listings
from routes.profile import profile

# Import models so Flask-Migrate can detect them.
from models import (
    School,
    Category,
    User,
    Item,
)


app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions.
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints.
app.register_blueprint(auth)
app.register_blueprint(marketplace)
app.register_blueprint(listings)
app.register_blueprint(profile)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
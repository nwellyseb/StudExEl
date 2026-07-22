from flask import Flask, render_template
from flask_migrate import Migrate

from config import Config
from extensions import csrf, db

from routes.auth import auth
from routes.listings import listings
from routes.marketplace import marketplace
from routes.moderation import moderation
from routes.messages import messages
from routes.profile import profile
from routes.reports import reports

# Import models so Flask-Migrate can detect them.
from models import (
    Category,
    Conversation,
    Item,
    Message,
    Report,
    School,
    User,
)


app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions.
db.init_app(app)
csrf.init_app(app)

migrate = Migrate(
    app,
    db,
)


# Register blueprints.
app.register_blueprint(auth)
app.register_blueprint(marketplace)
app.register_blueprint(listings)
app.register_blueprint(messages)
app.register_blueprint(moderation)
app.register_blueprint(profile)
app.register_blueprint(reports)


@app.route("/")
def home():

    return render_template(
        "home.html"
    )


@app.errorhandler(400)
def bad_request(error):

    return render_template(
        "errors/400.html"
    ), 400


@app.errorhandler(413)
def file_too_large(error):

    return render_template(
        "errors/413.html"
    ), 413


if __name__ == "__main__":

    app.run(
        debug=True
    )
import sys
from pathlib import Path

import pytest
from flask import Flask, render_template


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_DIR),
)


from extensions import csrf, db

from models import (
    Category,
    Conversation,
    Item,
    Message,
    School,
    User,
)

from routes.auth import auth
from routes.listings import listings
from routes.marketplace import marketplace
from routes.moderation import moderation
from routes.messages import messages
from routes.profile import profile
from routes.reports import reports


@pytest.fixture
def app(tmp_path):

    test_app = Flask(
        __name__,
        template_folder=str(
            BACKEND_DIR / "templates"
        ),
        static_folder=str(
            BACKEND_DIR / "static"
        ),
    )

    test_database = (
        tmp_path / "studexel_test.db"
    )

    test_upload_folder = (
        tmp_path / "uploads"
    )

    test_app.config.update(
        TESTING=True,
        SECRET_KEY="studexel-test-key",
        SQLALCHEMY_DATABASE_URI=(
            f"sqlite:///{test_database}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False,
        ITEM_IMAGE_UPLOAD_FOLDER=str(
            test_upload_folder
        ),
        MAX_CONTENT_LENGTH=(
            5 * 1024 * 1024
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )

    db.init_app(
        test_app
    )

    csrf.init_app(
        test_app
    )

    test_app.register_blueprint(
        auth
    )

    test_app.register_blueprint(
        marketplace
    )

    test_app.register_blueprint(
        listings
    )

    test_app.register_blueprint(
        messages
    )

    test_app.register_blueprint(
        profile
    )
    test_app.register_blueprint(reports)
    test_app.register_blueprint(moderation)

    @test_app.route("/")
    def home():

        return render_template(
            "home.html"
        )

    with test_app.app_context():

        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):

    return app.test_client()


@pytest.fixture
def runner(app):

    return app.test_cli_runner()


@pytest.fixture
def school(app):

    test_school = School(
        school_name=(
            "StudExEl Test University"
        ),
        short_name="STU",
        school_type="University",
        sector="Private",
        region="Test Region",
        city="Test City",
        is_active=True,
    )

    db.session.add(
        test_school
    )

    db.session.commit()

    return test_school


@pytest.fixture
def category(app):

    test_category = Category(
        category_name="Textbooks",
        slug="textbooks",
        description=(
            "Books and academic materials."
        ),
        display_order=1,
        is_active=True,
    )

    db.session.add(
        test_category
    )

    db.session.commit()

    return test_category


@pytest.fixture
def user(app, school):

    test_user = User(
        first_name="Test",
        last_name="Student",
        username="teststudent",
        email="teststudent@example.com",
        school_id=school.id,
    )

    test_user.set_password(
        "securepassword123"
    )

    db.session.add(
        test_user
    )

    db.session.commit()

    return test_user


@pytest.fixture
def logged_in_client(
    client,
    user,
):

    response = client.post(
        "/login",
        data={
            "username": user.username,
            "password": (
                "securepassword123"
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    return client


@pytest.fixture
def second_user(
    app,
    school,
):

    test_user = User(
        first_name="Another",
        last_name="Student",
        username="anotherstudent",
        email="anotherstudent@example.com",
        school_id=school.id,
    )

    test_user.set_password(
        "anotherpassword123"
    )

    db.session.add(
        test_user
    )

    db.session.commit()

    return test_user


@pytest.fixture
def second_logged_in_client(
    client,
    second_user,
):

    response = client.post(
        "/login",
        data={
            "username": (
                second_user.username
            ),
            "password": (
                "anotherpassword123"
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    return client

from datetime import UTC, datetime

from extensions import db
from models.user import User


def create_test_user(
    app,
    school,
    username="teststudent",
    email="teststudent@example.com",
):

    with app.app_context():

        user = User(
            first_name="Test",
            last_name="Student",
            username=username,
            email=email,
            email_verified_at=(
                datetime.now(UTC).replace(tzinfo=None)
            ),
            school_id=school.id,
        )

        user.set_password(
            "securepassword123"
        )

        db.session.add(user)
        db.session.commit()

        return user.id


def test_user_can_register(
    client,
    app,
    school,
):

    response = client.post(
        "/register",
        data={
            "first_name": "Test",
            "last_name": "Student",
            "username": "teststudent",
            "email": "teststudent@example.com",
            "school": str(school.id),
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "agree_terms": "y",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Account created. Check your email"
        in response.data
    )

    with app.app_context():

        user = User.query.filter_by(
            username="teststudent"
        ).first()

        assert user is not None

        assert (
            user.email
            == "teststudent@example.com"
        )

        assert user.school_id == school.id

        assert user.check_password(
            "securepassword123"
        )


def test_user_can_login(
    client,
    app,
    school,
):

    user_id = create_test_user(
        app,
        school,
    )

    response = client.post(
        "/login",
        data={
            "username": "teststudent",
            "password": "securepassword123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Welcome back, Test!"
        in response.data
    )

    with client.session_transaction() as session:

        assert session["user_id"] == user_id


def test_login_rejects_invalid_password(
    client,
    app,
    school,
):

    create_test_user(
        app,
        school,
    )

    response = client.post(
        "/login",
        data={
            "username": "teststudent",
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Invalid username or password."
        in response.data
    )

    with client.session_transaction() as session:

        assert "user_id" not in session


def test_logged_in_user_can_logout(
    client,
    app,
    school,
):

    create_test_user(
        app,
        school,
    )

    client.post(
        "/login",
        data={
            "username": "teststudent",
            "password": "securepassword123",
        },
    )

    response = client.get(
        "/logout",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"You have been logged out."
        in response.data
    )

    with client.session_transaction() as session:

        assert "user_id" not in session


def test_registration_sends_verification_email(
    client,
    app,
    school,
):

    response = client.post(
        "/register",
        data={
            "first_name": "Email",
            "last_name": "Student",
            "username": "emailstudent",
            "email": "emailstudent@example.com",
            "school": str(school.id),
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "agree_terms": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    outbox = app.extensions[
        "email_outbox"
    ]

    assert len(outbox) == 1

    message = outbox[0]

    assert message["to"] == [
        "emailstudent@example.com"
    ]

    assert (
        message["subject"]
        == "Verify your StudExEl email"
    )

    assert (
        "/verify-email/"
        in message["text"]
    )

    with app.app_context():

        user = User.query.filter_by(
            username="emailstudent"
        ).first()

        assert user is not None
        assert user.email_verified_at is None


def test_unverified_user_cannot_log_in(
    client,
    app,
    school,
):

    with app.app_context():

        user = User(
            first_name="Pending",
            last_name="Student",
            username="pendingstudent",
            email="pendingstudent@example.com",
            school_id=school.id,
        )

        user.set_password(
            "securepassword123"
        )

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "username": "pendingstudent",
            "password": "securepassword123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Verify your email before logging in."
        in response.data
    )

    with client.session_transaction() as session:

        assert "user_id" not in session


def test_user_can_verify_email(
    client,
    app,
    school,
):

    from utils.auth_tokens import (
        generate_email_verification_token,
    )

    with app.app_context():

        user = User(
            first_name="Verify",
            last_name="Student",
            username="verifystudent",
            email="verifystudent@example.com",
            school_id=school.id,
        )

        user.set_password(
            "securepassword123"
        )

        db.session.add(user)
        db.session.commit()

        user_id = user.id

        token = (
            generate_email_verification_token(
                user
            )
        )

    response = client.get(
        f"/verify-email/{token}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your email has been verified."
        in response.data
    )

    with app.app_context():

        user = db.session.get(
            User,
            user_id,
        )

        assert user.email_verified_at is not None


def test_forgot_password_uses_generic_response(
    client,
    app,
):

    response = client.post(
        "/forgot-password",
        data={
            "email": "unknown@example.com",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"If an eligible account exists"
        in response.data
    )

    assert (
        app.extensions.get(
            "email_outbox",
            [],
        )
        == []
    )


def test_verified_user_receives_reset_email(
    client,
    app,
    school,
):

    create_test_user(
        app,
        school,
    )

    response = client.post(
        "/forgot-password",
        data={
            "email": "teststudent@example.com",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    outbox = app.extensions[
        "email_outbox"
    ]

    assert len(outbox) == 1

    assert (
        outbox[0]["subject"]
        == "Reset your StudExEl password"
    )

    assert (
        "/reset-password/"
        in outbox[0]["text"]
    )


def test_user_can_reset_password(
    client,
    app,
    school,
):

    from utils.auth_tokens import (
        generate_password_reset_token,
    )

    user_id = create_test_user(
        app,
        school,
    )

    with app.app_context():

        user = db.session.get(
            User,
            user_id,
        )

        token = (
            generate_password_reset_token(
                user
            )
        )

    response = client.post(
        f"/reset-password/{token}",
        data={
            "password": "newsecurepassword456",
            "confirm_password": (
                "newsecurepassword456"
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your password has been reset."
        in response.data
    )

    with app.app_context():

        user = db.session.get(
            User,
            user_id,
        )

        assert user.check_password(
            "newsecurepassword456"
        )

        assert not user.check_password(
            "securepassword123"
        )

    reused_response = client.get(
        f"/reset-password/{token}",
        follow_redirects=True,
    )

    assert (
        b"invalid or has expired"
        in reused_response.data
    )


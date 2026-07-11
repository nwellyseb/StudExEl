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
        b"Account created successfully"
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
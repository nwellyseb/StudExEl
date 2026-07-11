from extensions import db
from models.user import User


def registration_data(
    school,
    username="teststudent",
    email="teststudent@example.com",
):

    return {
        "first_name": "Test",
        "last_name": "Student",
        "username": username,
        "email": email,
        "school": str(school.id),
        "password": "securepassword123",
        "confirm_password": "securepassword123",
        "agree_terms": "y",
    }


def test_duplicate_username_is_rejected(
    client,
    app,
    school,
):

    client.post(
        "/register",
        data=registration_data(
            school,
            username="duplicateuser",
            email="first@example.com",
        ),
    )

    response = client.post(
        "/register",
        data=registration_data(
            school,
            username="duplicateuser",
            email="second@example.com",
        ),
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Username already exists."
        in response.data
    )

    with app.app_context():

        users = db.session.execute(
            db.select(User).where(
                User.username == "duplicateuser"
            )
        ).scalars().all()

        assert len(users) == 1


def test_duplicate_email_is_rejected(
    client,
    app,
    school,
):

    client.post(
        "/register",
        data=registration_data(
            school,
            username="firstuser",
            email="duplicate@example.com",
        ),
    )

    response = client.post(
        "/register",
        data=registration_data(
            school,
            username="seconduser",
            email="duplicate@example.com",
        ),
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Email already exists."
        in response.data
    )

    with app.app_context():

        users = db.session.execute(
            db.select(User).where(
                User.email == "duplicate@example.com"
            )
        ).scalars().all()

        assert len(users) == 1
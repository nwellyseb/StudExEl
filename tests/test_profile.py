from extensions import db
from models.user import User


def test_logged_in_user_can_view_profile(
    logged_in_client,
    user,
):

    response = logged_in_client.get(
        "/profile"
    )

    assert response.status_code == 200

    assert (
        user.username.encode()
        in response.data
    )

    assert (
        user.email.encode()
        in response.data
    )


def test_logged_in_user_can_update_profile(
    logged_in_client,
    app,
    user,
):

    response = logged_in_client.post(
        "/profile/edit",
        data={
            "course": "Computer Science",
            "year_level": "3rd Year",
            "bio": (
                "Student interested in programming "
                "and marketplace development."
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Profile updated successfully!"
        in response.data
    )

    with app.app_context():

        updated_user = db.session.get(
            User,
            user.id,
        )

        assert updated_user is not None

        assert (
            updated_user.course
            == "Computer Science"
        )

        assert (
            updated_user.year_level
            == "3rd Year"
        )

        assert updated_user.bio == (
            "Student interested in programming "
            "and marketplace development."
        )

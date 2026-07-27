from io import BytesIO
from unittest.mock import patch

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



def test_pending_student_can_submit_verification(
    logged_in_client,
    app,
    user,
):
    with app.app_context():

        pending_user = db.session.get(
            User,
            user.id,
        )

        pending_user.verification_status = "Pending"

        pending_user.verification_document_public_id = None
        pending_user.verification_document_format = None

        db.session.commit()

    document = BytesIO(
        b"studexel-student-id-test"
    )

    with patch(
        "routes.profile.save_verification_document",
        return_value={
            "public_id": (
                "studexel/verifications/test-document"
            ),
            "format": "png",
        },
    ) as save_document:

        response = logged_in_client.post(
            "/verification/submit",
            data={
                "document": (
                    document,
                    "student-id.png",
                ),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    assert response.status_code == 200

    assert (
        b"Student verification submitted successfully."
        in response.data
    )

    save_document.assert_called_once()

    with app.app_context():

        submitted_user = db.session.get(
            User,
            user.id,
        )

        assert (
            submitted_user.verification_status
            == "Pending"
        )

        assert (
            submitted_user.verification_document_public_id
            == "studexel/verifications/test-document"
        )

        assert (
            submitted_user.verification_document_format
            == "png"
        )

        assert (
            submitted_user.verification_submitted_at
            is not None
        )

        assert (
            submitted_user.verification_rejection_reason
            is None
        )


def test_verified_student_cannot_resubmit_verification(
    logged_in_client,
):

    response = logged_in_client.get(
        "/verification/submit",
        follow_redirects=True,
    )

    assert response.status_code == 200

    assert (
        b"Your student account is already verified."
        in response.data
    )
